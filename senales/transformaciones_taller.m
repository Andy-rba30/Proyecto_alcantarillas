%% CUATRO TRANSFORMACIONES CONCRETAS
%     y1(t) =    x(t + 4)
%     y2(t) =   -x(-3t - 4)
%     y3(t) = -5*x(-0.5t + 1)
%     y4(t) =  3*x(10t - 2)
%
%  Mismo esquema que transformaciones.m: la señal es una función anónima y
%  cada transformación la llama con otro argumento. Cambian solo los ajustes,
%  porque estas cuatro no caben en la ventana por defecto:
%     y3 tiene amplitud 5 y se extiende hasta t = -8.7
%     y4 esta comprimida 10 veces, asi que hace falta mucho mas muestreo

clear; clc; close all;

% --- 1. Señal original ---------------------------------------------------
nombre = 'e^{-t} sen(2\pi t) u(t)';
x = @(t) exp(-t) .* sin(2*pi*t) .* (t >= 0);

t = linspace(-9, 3, 24000);   % ancho por y3, denso por y4

% --- 2. Las cuatro: {titulo, función anónima, ventana de detalle} --------
lista = {
    'y_1(t) = x(t+4)',         @(t)     x(t + 4),        [-4.6  0.6];
    'y_2(t) = -x(-3t-4)',      @(t)    -x(-3*t - 4),     [-2.9 -1.1];
    'y_3(t) = -5x(-0.5t+1)',   @(t)  -5*x(-0.5*t + 1),   [-9.0  2.6];
    'y_4(t) = 3x(10t-2)',      @(t)   3*x(10*t - 2),     [ 0.1  0.8]};

% --- 3. Dos figuras: comparación y detalle -------------------------------
%  Figura 1: las cuatro en la misma ventana y a la misma escala. Sirve para
%            comparar dónde cae cada una y cuánto crece.
%  Figura 2: cada una en su propia ventana y escala. Sirve para ver la forma,
%            sobre todo la de y4, que en la ventana común es una aguja.

titulos = {'Las cuatro a la misma escala (comparables)', ...
           'Cada una en su ventana (para ver la forma)'};

for f = 1:2
    figure('Color', 'w', 'Position', [40 + 30*f, 60, 1000, 640]);

    for k = 1:size(lista, 1)
        titulo   = lista{k, 1};
        y        = lista{k, 2};
        ventana  = lista{k, 3};

        subplot(2, 2, k);
        plot(t([1 end]), [0 0], 'k', 'LineWidth', 0.5);     % eje horizontal
        hold on;
        h1 = plot(t, x(t), '--', 'Color', [0.7 0.7 0.7], 'LineWidth', 1);
        h2 = plot(t, y(t), 'r', 'LineWidth', 1.6);
        hold off;

        if f == 1
            xlim([-9 3]); ylim([-4.4 4.4]);                 % común
        else
            xlim(ventana);                                  % propia
            dentro = (t >= ventana(1)) & (t <= ventana(2)); % escala a su medida
            m = max(abs(y(t(dentro))));
            ylim(1.25 * [-m m]);
        end

        if k == 1
            legend([h1 h2], 'x(t) original', 'transformada', ...
                   'Location', 'northwest', 'FontSize', 8);
        end

        title(titulo, 'Interpreter', 'none', 'FontSize', 11);
        xlabel('t [s]'); ylabel('amplitud');
        grid on;
    end

    if exist('sgtitle', 'file')
        sgtitle([titulos{f} '     x(t) = ' nombre], 'FontSize', 13);
    end
end
