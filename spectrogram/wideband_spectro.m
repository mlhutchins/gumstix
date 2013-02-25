%read in the wideband VLF data file
%     fid=fopen('WB20120624191600.dat'); % Null Case
    fid=fopen('WB20130219000000.dat'); % Whistler 1
%     fid=fopen('WB20130219003000.dat'); % Whistler 2

    unixTime = fread(fid,1,'int');  %seconds since 1 Jan 1970
    Fs= fread(fid,1,'double');  %precise sampling rate
    offsetSamples = fread(fid,1,'double');
    %y=fread(fid,[1,inf],'float');
    y=fread(fid,[1,inf],'short');
    y = y/32768;
    fclose(fid);

    %optional HP filter
    %hpf=fir1(64,400/Fs,'high');
    %y=filtfilt(hpf,1,y);

    %compute wideband timebase
    t=(0:1:length(y)-1);
    t=t+offsetSamples;
    t = t/Fs;

%% Spectogram

    % Set power spectra control variables
    Nw = 2^10; % Hanning window length
    Ny = length(y); % Ice sample length
    
    % Create Hanning window
    j = 1:Nw; % Set up an index vector to make hanning window
    w = 0.5*(1-cos(2*pi*(j-1)/Nw))'; % Make hanning window
    varw = 3/8; % Set mean-square power of taper function

    % Get full and half windowed data
    nwinf = floor(Ny/Nw); % Number of full windows
    nwinh = nwinf - 1;    % Number of half windows
    nwin = nwinf+nwinh; % Total number of windows

    yw = zeros(Nw,nwin);  % Initialize array for windowed data
    yw(:,1:2:nwin) = reshape(y(1:nwinf*Nw),Nw,nwinf); % Insert full windows
    yw(:,2:2:(nwin-1)) = reshape(y((1+Nw/2):(nwinf-0.5)*Nw),Nw,nwinh); %Insert half windows

    % Taper the data
    yt = repmat(w,[1 nwin]).*yw;

    % DFT and power spectrum of each column
    ythat = fft(yt); % FFT of data 
    S = (abs(ythat/Nw).^2)/varw; % Power spectrum, normalized by Hanning window power
    S = S(1:Nw/2,:);  % Remove negative harmonics
    SdB = 10*log10(S); % Switch to decibel scale
    Mw = 0:(Nw/2 - 1);  % Get harmonic
    fw = Fs*Mw/Nw; % Convert harmonics to frequencies
    tw = (1:nwin)*0.5*Nw/Fs; % Time of each window

%% Plot the power spectra
%     figure

    % Adds pads to data so pcolor is centered correctly
    dfw = fw(2)-fw(1);
    dtw = tw(2)-tw(1);
    fwpad = [fw fw(end)+dfw]-0.5*dfw;
    twpad = [tw tw(end)+dtw]-0.5*dtw;
    SdBpad = SdB([1:end end],[1:end end]);
    
    subplot(2,1,1)
    
    % Plot with pcolor
    pcolor(twpad,fwpad,SdBpad)
    
    % Format plot and add a colorbar
    xlabel('Time')
    ylabel('Frequency')
    shading flat
    c = colorbar;
    ylabel(c,'Spectral Power (dB)')
    
%% Whistler time for a specific file

    subplot(2,1,2)
    
    % Plot with pcolor
    pcolor(twpad,fwpad,SdBpad)
    
    % Format plot and add a colorbar
    xlabel('Time')
    ylabel('Frequency')
    shading flat
    c = colorbar;
    ylabel(c,'Spectral Power (dB)')
    xlim([16 19.5])
    

%% Find Whistlers

    band = sum(SdB(fw>4000 & fw<4500,:));
    
    window = 100;
    innerWindow = 10;
    threshold = 4;
    
    n=20;
    band = filter(ones(1,n)/n,1,band);
    band = band - min(band);
    band = band(20:end);

    high = false(length(band),1);
    highSum = high + 0;
    for i = window + 1 : length(high) - window
        
        bandWindow = band(i - window : i + window);
        bandWindow = bandWindow - min(bandWindow);
        
        prePower = threshold * mean(bandWindow(1 : window - innerWindow));
        postPower = threshold * mean(bandWindow(window + innerWindow : end));
        
        if bandWindow(window) > prePower && bandWindow(window) > postPower
            high(i) = true;
        else
            high(i) = false;
        end
        
        if high(i)
            highSum(i) = highSum(i-1) + high(i);
        end
        
        
    end

    timeStep = tw(2) - tw(1);
    whistlerTest = highSum > round(0.05/timeStep);
    
    
    figure
        subplot(3,1,1)
    
    % Plot with pcolor
    pcolor(twpad,fwpad,SdBpad)
    
    % Format plot and add a colorbar
    xlabel('Time')
    ylabel('Frequency')
    shading flat
%     c = colorbar;
%     ylabel(c,'Spectral Power (dB)')
    
    subplot(3,1,2)
    plot(band)
    xlim([0 length(band)])
    subplot(3,1,3)
    plot(whistlerTest)

    xlim([0 length(band)])

    
    
    
    
    
