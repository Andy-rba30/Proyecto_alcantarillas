%% GRAFICACION DE SEÑALES Y TRANSFORMACIONES
%  Grafica una señal x(t) y sus transformaciones en amplitud y en tiempo.
%  Cada transformación es una función anónima @(t)..., que es el equivalente
%  en MATLAB a una función lambda.
%
%     y(t) = A*x(a*t + b) + B        A, B -> amplitud        a, b -> tiempo

clear; clc; close all;

% --- 1. Señal original ---------------------------------------------------
%  Al ser una función anónima y no un vector, se puede evaluar en CUALQUIER
%  argumento: x(t), x(2*t), x(-t)... y de ahí salen las transformaciones.
%  Cambia estas dos líneas para probar con otra señal.
nombre = 'e^{-t} sen(2\pi t) u(t)';
x = @(t) exp(-t) .* sin(2*pi*t) .* (t >= 0);

t = linspace(-5, 5, 1000);          % eje de tiempo: 1000 puntos entre -5 y 5

% --- 2. Transformaciones: cada fila es {titulo, función anónima} ---------
lista = {
    'Original:  x(t)',                  @(t)  x(t);
    'Amplificación:  2*x(t)',           @(t)  2*x(t);
    'Reflexión en amplitud:  -x(t)',    @(t) (-x(t));
    'Desplazamiento vertical:  x(t)+1', @(t)  x(t) + 1;
    'Retardo:  x(t-2)',                 @(t)  x(t - 2);
    'Adelanto:  x(t+2)',                @(t)  x(t + 2);
    'Reflexión en el tiempo:  x(-t)',   @(t)  x(-t);
    'Compresión:  x(2t)',               @(t)  x(2*t);
    'Expansión:  x(t/2)',               @(t)  x(t/2)
    };

% --- 3. Una gráfica por transformación -----------------------------------
figure('Color', 'w', 'Position', [60 50 1150 720]);

for k = 1:size(lista, 1)
    titulo = lista{k, 1};
    y      = lista{k, 2};

    subplot(3, 3, k);
    plot([-5 5], [0 0], 'k', 'LineWidth', 0.5);        % ejes de referencia
    hold on;
    plot([0 0], [-2.2 2.2], 'k', 'LineWidth', 0.5);
    h1 = plot(t, x(t), '--', 'Color', [0.7 0.7 0.7], 'LineWidth', 1);  % original
    h2 = plot(t, y(t), 'r', 'LineWidth', 2);                           % transformada
    hold off;

    if k == 1
        legend([h1 h2], 'original', 'transformada', 'Location', 'northeast', 'FontSize', 8);
    end

    title(titulo, 'Interpreter', 'none', 'FontSize', 10);
    xlabel('t [s]'); ylabel('amplitud');
    xlim([-5 5]); ylim([-2.2 2.2]);
    grid on;
end

if exist('sgtitle', 'file')         % sgtitle existe desde R2018b
    sgtitle(['Señal  x(t) = ' nombre '   y sus transformaciones'], 'FontSize', 13);
end
