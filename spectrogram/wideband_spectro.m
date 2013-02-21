%read in the wideband VLF data file
    fid=fopen('WBTest.dat');
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
    Ny = length(yShort); % Ice sample length
    
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

    % Plot the power spectra
%     figure

    % Adds pads to data so pcolor is centered correctly
    dfw = fw(2)-fw(1);
    dtw = tw(2)-tw(1);
    fwpad = [fw fw(end)+dfw]-0.5*dfw;
    twpad = [tw tw(end)+dtw]-0.5*dtw;
    SdBpad = SdB([1:end end],[1:end end]);
    
    % Plot with pcolor
    pcolor(twpad,fwpad,SdBpad)
    
    % Format plot and add a colorbar
    xlabel('Time')
    ylabel('Frequency')
    shading flat
    c = colorbar;
    ylabel(c,'Spectral Power (dB)')
    
