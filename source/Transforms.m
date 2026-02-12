function Transforms()
% Transforms example. 
% The Fourier transform and Hodrick-Prescott filters are part of MATLAB
% toolboxes, but they have been implemented here to demosntrate how these
% techniques work. 
% By Juan B. Gutierrez, Professor of Mathematics
% @biomathematicus - juan.gutierrez3@utsa.edu
    clear;
    % First, produce a random time series with trend
    x = (0:.01:3*pi)';
    n = size(x,1);
    s = std( cos(x).*x)/rand(); 
    f = cos(x).*x + s*rand(n,1);
    % Set parameters for smoothing
    m = 10; % Number of Fourier frequencies to preserve. 
    maw = 20; % moving average window
    lambda  = 100000; % HP filter smoothing parameter.
    % Now, produce smooth time series 
    y1 = FFTExercise(m,x,f); 
    y2 = SmoothFourier(m,x,f); 
    y3 = HodrickPrescott(f,lambda);  
    y4 = funMovingAverage(f, maw);
    % Visualize original function
    clf;     figure(1);
    plot(x,f,'color',[.6 .6 .6]); 
    hold on
    plot(x, y1, 'k-', 'linewidth',1.5);
    plot(x, y2, 'b', 'linewidth',3);
    plot(x, y3, 'r', 'linewidth',1.5);
    plot(x(maw:end), y4(maw:end), 'k', 'linewidth',1.5);
    legend('Raw','Manual Fourier Transform', 'MATLAB FFT Function','HP', 'Moving Average');
    %legend('Raw Data','Hodrick-Prescott', 'Moving Average');
    title('Function smoothing comparisons'); 
    axis tight;
    hold off
    
end

function y1 = FFTExercise(m,x,f)
    n = size(x,1);
    % Calculate the elements of the discrete Fourier Transform
    % This can be done with MATLAB's fft function; this is just an exercise
    w = exp(2*pi*j/n);
    for i=0:n-1
        for k=i:n-1
            F(i+1,k+1) = w^(i*k);
            F(k+1,i+1) = F(i+1,k+1);
        end
    end
    T = F*f;
    
    % Now filter out frequencies. Leave only m frequencies
    B = sort(T,'descend');
    [~,uIdx] = ismember(T,B); % Index to reverse sort: f = B(uIdx)
    idx = m+1:n;
    B(idx) = 0;
    T = B(uIdx);  
    
    % Calculate the inverse Fourier transform
    % This can be done with MATLAB's ifft function; this is just an exercise
    w = exp(-2*pi*j/n);
    for i=0:n-1
        for k=i:n-1
            iF(i+1,k+1) = w^(i*k);
            iF(k+1,i+1) = iF(i+1,k+1);
        end
    end
    
    % Filter before inverting the transform
    y1 = real(iF*T)/n;
end

function y2 = SmoothFourier(m,x,f)
    % y = raw data vector
    % m = frequencies that we want to keep
    y2 = fft(f);
    n = size(f,1);
    B = sort(y2,'descend');
    [~,uIdx] = ismember(y2,B); % Index to reverse sort: f = B(uIdx)
    idx = m+1:n;
    B(idx) = 0;
    y2 = real(ifft(B(uIdx)));
end

function [s] = HodrickPrescott(y,w)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  Author: Ivailo Izvorski, 
%          Department of Economics
%	   Yale University.
%          izvorski@econ.yale.edu
%  This code has been used and seems to be free of error.
%  However, it carries no explicit or implicit guarantee.
%
%  function [s]=hpfilter(y,w)
%  Hondrick Prescott filter where:
%  w - smoothing parameter; w=1600 for quarterly data
%  y - the original series that has to be smoothed
%  s - the filtered series
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    if size(y,1)<size(y,2)
       y=y';
    end
    t=size(y,1);
    a=6*w+1;
    b=-4*w;
    c=w;
    d=[c,b,a];
    d=ones(t,1)*d;
    m=diag(d(:,3))+diag(d(1:t-1,2),1)+diag(d(1:t-1,2),-1);
    m=m+diag(d(1:t-2,1),2)+diag(d(1:t-2,1),-2);
    %
    m(1,1)=1+w;       m(1,2)=-2*w;
    m(2,1)=-2*w;      m(2,2)=5*w+1;
    m(t-1,t-1)=5*w+1; m(t-1,t)=-2*w;
    m(t,t-1)=-2*w;    m(t,t)=1+w;
    %
    s=m \ y; % only modification with respect to original file
end

function I = integrator(f,a,b)
    I = 0;
    n = size(f,1);
    dx = (b-a)/n;
    for i=2:n
        I = I + (f(i-1)+f(i))/2*dx;
    end
end

function m = funMovingAverage(A, maw)
    m=ones(1,length(A));
    for i=1:length(A)
        if i <= maw
            m(i) = A(i);
        else
            m(i) = mean(A(i-maw:i));
        end
    end
end