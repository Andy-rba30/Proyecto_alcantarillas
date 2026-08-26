function transformacion_senales
%TRANSFORMACION_SENALES  Transformación de señales:  y(t) = A*x(a*t + b) + B
%
%  COMO SE USA
%    Abre este archivo en MATLAB y pulsa Run (o escribe transformacion_senales
%    en la Command Window). Todo se elige desde el menú: no hay que tocar el
%    código para cambiar de señal.
%
%  QUE HACE
%    1) Eliges la señal x(t) de una lista (o escribes la tuya).
%    2) Eliges modo guiado (escribes los 4 números) o interactivo (deslizadores).
%    3) El programa DICE EN PALABRAS qué operación hace cada coeficiente y en
%       qué orden, en la Command Window y dentro de la propia figura.
%    4) Grafica la original y la transformada superpuestas, con el eje de
%       tiempo ajustado para que no se corte nada.
%
%  LOS CUATRO COEFICIENTES
%    A  amplitud     1 = igual   2 = el doble        -1 = la invierte
%    a  tiempo       1 = igual   2 = la comprime      0.5 = la ensancha   -1 = la espeja
%    b  corrimiento  0 = igual  +2 = 2 a la izquierda  -2 = 2 a la derecha
%    B  nivel        0 = igual  +1 = la sube 1        -1 = la baja 1
%
%    Con A=1, a=1, b=0, B=0 la señal no cambia. Pulsar Enter deja el valor
%    anterior, así que nunca se rompe por darle a Enter sin escribir nada.

clc; close all;

cabecera();
[x, expr] = elegir_senal();
modo      = elegir_modo();

if modo == 2
    modo_interactivo(x, expr);
    return
end

% ---------- modo guiado ------------------------------------------------
A = 1; a = 1; b = 0; B = 0;
fig = [];
while true
    [A, a, b, B] = pedir_coeficientes(A, a, b, B);
    resumen = resumen_texto(expr, A, a, b, B);
    imprimir_lineas(resumen);
    fig = graficar(fig, x, expr, A, a, b, B, resumen);

    fprintf('\n   [Enter] otra transformación    [c] cambiar de señal    [q] salir\n');
    r = lower(strtrim(input('   > ', 's')));
    if strcmp(r, 'q') || strcmp(r, 'n')
        break
    elseif strcmp(r, 'c')
        [x, expr] = elegir_senal();
    end
end
fprintf('\n   Listo.\n\n');
end


% =======================================================================
%  MENUS Y LECTURA DE DATOS
% =======================================================================
function cabecera()
fprintf('\n');
fprintf('   ============================================================\n');
fprintf('    TRANSFORMACION DE SENALES      y(t) = A*x(a*t + b) + B\n');
fprintf('   ============================================================\n');
end


function [f, expr] = elegir_senal()
catalogo = { ...
    'exp(-t.^2).*cos(pi*t)'    'gaussiana modulada'
    'double(abs(t) <= 1)'      'pulso rectangular de ancho 2'
    'max(0, 1 - abs(t))'       'triángulo de base 2'
    'double(t >= 0)'           'escalón unitario u(t)'
    'exp(-t).*double(t >= 0)'  'exponencial decreciente causal'
    'sin(pi*t)'                'senoidal'};

n = size(catalogo, 1);
fprintf('\n   ¿Qué señal x(t) quieres usar?\n\n');
for k = 1:n
    fprintf('     %d) x(t) = %-24s  %s\n', k, catalogo{k,1}, catalogo{k,2});
end
fprintf('     %d) escribir mi propia expresión\n\n', n+1);

k = leer_entero('Opción', 1, 1, n+1);
if k <= n
    expr = catalogo{k,1};
    f    = str2func(['@(t) ' expr]);
else
    [f, expr] = leer_expresion();
end
fprintf('\n   Señal elegida:  x(t) = %s\n', expr);
end


function [f, expr] = leer_expresion()
fprintf('\n   Escribe x(t) en función de t, con operadores CON PUNTO (.* ./ .^).\n');
fprintf('   Ejemplos:  exp(-t.^2).*cos(pi*t)     sin(2*pi*t)./(1+t.^2)\n\n');
while true
    expr = strtrim(input('   x(t) = ', 's'));
    if isempty(expr)
        expr = 'exp(-t.^2).*cos(pi*t)';
        fprintf('   (vacío: uso la de ejemplo, %s)\n', expr);
    end
    try
        f = str2func(['@(t) ' expr]);
        v = double(f(linspace(-1, 1, 5)));
        if isscalar(v) || numel(v) == 5
            return
        end
        fprintf('   Esa expresión no devuelve un vector del tamaño de t.\n');
    catch err
        fprintf('   No pude interpretarla: %s\n', err.message);
    end
    fprintf('   Recuerda el punto:  t.^2  en vez de t^2,  a.*b  en vez de a*b.\n\n');
end
end


function m = elegir_modo()
fprintf('\n   ¿Cómo quieres trabajar?\n\n');
fprintf('     1) Guiado: escribo A, a, b y B, y el programa explica y grafica\n');
fprintf('     2) Interactivo: muevo 4 deslizadores y la gráfica cambia sola\n\n');
m = leer_entero('Opción', 1, 1, 2);
end


function [A, a, b, B] = pedir_coeficientes(A, a, b, B)
fprintf('\n   ------------------------------------------------------------\n');
fprintf('    FORMULA:   y(t) = A*x(a*t + b) + B\n');
fprintf('   ------------------------------------------------------------\n');
fprintf('     A  amplitud     1 = igual,  2 = el doble,  -1 = la invierte\n');
fprintf('     a  tiempo       1 = igual,  2 = la comprime,  0.5 = la ensancha,  -1 = la espeja\n');
fprintf('     b  corrimiento  0 = igual,  +2 = 2 a la izquierda,  -2 = 2 a la derecha\n');
fprintf('     B  nivel        0 = igual,  +1 = la sube 1,  -1 = la baja 1\n\n');
fprintf('     Enter deja el valor entre corchetes. Se admite 3/4, pi/2, -0.5.\n\n');

s = strtrim(input('   Los 4 de una vez  "A a b B"  (o Enter para ir uno por uno): ', 's'));
v = a_vector(s);
if numel(v) == 4 && v(2) ~= 0
    A = v(1); a = v(2); b = v(3); B = v(4);
    fprintf('   -> A = %s,  a = %s,  b = %s,  B = %s\n', n2s(A), n2s(a), n2s(b), n2s(B));
    return
end
if ~isempty(s)
    fprintf('   (No leí 4 números válidos con a distinto de 0; los pido uno por uno.)\n');
end

fprintf('\n');
A = leer_numero('A  amplitud', A);
a_ant = a;                       % el defecto sigue siendo el ultimo valor VALIDO
while true
    a = leer_numero('a  escala de tiempo (distinta de 0)', a_ant);
    if a ~= 0
        break
    end
    fprintf('      Con a = 0 el tiempo desaparece y y(t) sale constante. Elige otro valor.\n');
end
b = leer_numero('b  corrimiento en el tiempo', b);
B = leer_numero('B  corrimiento vertical', B);
end


function v = leer_numero(etiqueta, defecto)
while true
    s = strtrim(input(sprintf('   %-38s [%s]: ', etiqueta, n2s(defecto)), 's'));
    if isempty(s)
        v = defecto;
        return
    end
    w = a_numero(s);
    if ~isnan(w)
        v = w;
        return
    end
    fprintf('      "%s" no es un número. Prueba 2, -0.5, 3/4 o pi/2  (Enter = %s).\n', s, n2s(defecto));
end
end


function k = leer_entero(etiqueta, defecto, lo, hi)
while true
    s = strtrim(input(sprintf('   %s [%d]: ', etiqueta, defecto), 's'));
    if isempty(s)
        k = defecto;
        return
    end
    k = round(str2double(s));
    if ~isnan(k) && k >= lo && k <= hi
        return
    end
    fprintf('      Escribe un número entre %d y %d  (Enter = %d).\n', lo, hi, defecto);
end
end


function v = a_numero(s)
% Acepta 2, -0.5, 3/4, pi/2 ... Devuelve NaN si no es un número real finito.
v = str2double(s);
if isscalar(v) && isreal(v) && isfinite(v)
    return
end
w = a_vector(s);
if numel(w) == 1
    v = w;
else
    v = NaN;
end
end


function v = a_vector(s)
% Convierte "2 -1 3 0" (o con comas) en [2 -1 3 0]. Devuelve [] si no puede.
v = [];
if isempty(s)
    return
end
try
    w = str2num(strrep(s, ',', ' ')); %#ok<ST2NM>
catch
    w = [];
end
if isnumeric(w) && isreal(w) && ~isempty(w) && all(isfinite(w(:)))
    v = w(:).';
end
end


% =======================================================================
%  EXPLICACION DE LA TRANSFORMACION  (esto es lo que antes faltaba)
% =======================================================================
function s = formula_texto(A, a, b, B)
% Devuelve la fórmula ya con los números puestos: "y(t) = 2*x(-t + 3) - 1"
if a == 1
    arg = 't';
elseif a == -1
    arg = '-t';
else
    arg = [n2s(a) '*t'];
end
if b > 0
    arg = [arg ' + ' n2s(b)];
elseif b < 0
    arg = [arg ' - ' n2s(abs(b))];
end

if A == 0
    cuerpo = '0';
elseif A == 1
    cuerpo = ['x(' arg ')'];
elseif A == -1
    cuerpo = ['-x(' arg ')'];
else
    cuerpo = [n2s(A) '*x(' arg ')'];
end

if B > 0
    s = ['y(t) = ' cuerpo ' + ' n2s(B)];
elseif B < 0
    s = ['y(t) = ' cuerpo ' - ' n2s(abs(B))];
else
    s = ['y(t) = ' cuerpo];
end
end


function pasos = pasos_transformacion(A, a, b, B)
% Lista, en orden de aplicación, qué le pasa a x(t) para llegar a y(t).
% El orden es: corrimiento en tiempo (b) -> escala/reflexión en tiempo (a)
% -> amplitud (A) -> nivel (B). Con ese orden el corrimiento vale b exacto.
pasos = {};

if b ~= 0
    if b > 0
        d = 'IZQUIERDA';
    else
        d = 'DERECHA';
    end
    pasos{end+1} = sprintf('Corrimiento en el tiempo: %s hacia la %s   [ x(t) -> x(t %s %s) ]', ...
        n2s(abs(b)), d, signo(b), n2s(abs(b)));
end

if a < 0
    pasos{end+1} = sprintf('Reflexión en el tiempo (t -> -t): la señal se recorre al revés');
end
if abs(a) > 1
    pasos{end+1} = sprintf('Compresión en el tiempo: queda %s veces más angosta', n2s(abs(a)));
elseif abs(a) < 1
    pasos{end+1} = sprintf('Expansión en el tiempo: queda %s veces más ancha', n2s(1/abs(a)));
end

if A == 0
    pasos{end+1} = sprintf('A = 0: la señal se anula por completo');
else
    if A < 0
        pasos{end+1} = sprintf('Reflexión en amplitud: se da vuelta arriba/abajo');
    end
    if abs(A) > 1
        pasos{end+1} = sprintf('Amplificación: la amplitud se multiplica por %s', n2s(abs(A)));
    elseif abs(A) < 1
        pasos{end+1} = sprintf('Atenuación: la amplitud queda al %s%% de la original', n2s(100*abs(A)));
    end
end

if B ~= 0
    if B > 0
        d = 'ARRIBA';
    else
        d = 'ABAJO';
    end
    pasos{end+1} = sprintf('Corrimiento vertical: %s hacia %s', n2s(abs(B)), d);
end

if isempty(pasos)
    pasos = {'Ninguna: A=1, a=1, b=0, B=0 son los valores neutros, y(t) = x(t)'};
end
end


function L = resumen_texto(expr, A, a, b, B)
L = {};
L{end+1} = sprintf('SENAL ORIGINAL     x(t) = %s', expr);
L{end+1} = sprintf('TRANSFORMADA       %s', formula_texto(A, a, b, B));
L{end+1} = sprintf('                   A = %s    a = %s    b = %s    B = %s', ...
                   n2s(A), n2s(a), n2s(b), n2s(B));
L{end+1} = '';
L{end+1} = 'QUE SE LE HACE A x(t), EN ESTE ORDEN:';
pasos = pasos_transformacion(A, a, b, B);
for k = 1:numel(pasos)
    L{end+1} = sprintf('   %d) %s', k, pasos{k}); %#ok<AGROW>
end
if b ~= 0
    L{end+1} = '';
    L{end+1} = sprintf('COMPROBACION: lo que en x(t) ocurria en t = 0, en y(t) ocurre en t = %s', n2s(-b/a));
end
if a ~= 1 && b ~= 0
    L{end+1} = sprintf('OJO CON EL ORDEN: corriendo primero, el corrimiento es b = %s;', n2s(b));
    L{end+1} = sprintf('   si escalas primero y corres despues, vale b/a = %s.', n2s(b/a));
end
end


% =======================================================================
%  CALCULO Y GRAFICA
% =======================================================================
function v = evaluar_senal(f, t)
v = double(f(t));
if isscalar(v)
    v = v * ones(size(t));
end
if numel(v) ~= numel(t)
    error('transformacion:senal', ...
        'La expresión de x(t) no devuelve un vector del tamaño de t. Usa .*  ./  .^');
end
v = reshape(v, size(t));
end


function [t, xt, yt] = evaluar(x, A, a, b, B)
% Ventana natural de la señal original y ventana donde cae la transformada,
% para que el corrimiento o la expansión no queden fuera de la gráfica.
base = [-5 5];
lim  = sort((base - b) / a);
tmin = max(min(base(1), lim(1)), -50);
tmax = min(max(base(2), lim(2)),  50);
if ~isfinite(tmin) || ~isfinite(tmax) || tmax <= tmin
    tmin = -5; tmax = 5;
end
t  = linspace(tmin, tmax, 2000);
xt = evaluar_senal(x, t);
yt = A * evaluar_senal(x, a*t + b) + B;
end


function fig = graficar(fig, x, expr, A, a, b, B, resumen)
[t, xt, yt] = evaluar(x, A, a, b, B);
formula = formula_texto(A, a, b, B);

if isempty(fig) || ~ishandle(fig)
    fig = figure('Name', 'Transformación de señales', 'NumberTitle', 'off', 'Color', 'w');
    p = get(fig, 'Position');
    set(fig, 'Position', [p(1) max(p(2)-160, 50) 900 700]);
else
    clf(fig);
    delete(findall(fig, 'Tag', 'panel_resumen'));
    figure(fig);
end

vals = [xt(:); yt(:)];
vals = vals(isfinite(vals));
if isempty(vals)
    vals = [0; 1];
end
lo = min(vals); hi = max(vals);
if hi - lo < 1e-12
    lo = lo - 1; hi = hi + 1;
end
yl = [lo - 0.15*(hi-lo), hi + 0.15*(hi-lo)];
xl = [t(1) t(end)];

ax1 = axes('Parent', fig, 'Position', [0.09 0.775 0.87 0.165]);
plot(ax1, t, xt, 'b', 'LineWidth', 2);
grid(ax1, 'on'); xlim(ax1, xl); ylim(ax1, yl);
set(ax1, 'XTickLabel', []);          % el eje t se rotula abajo, una sola vez
ylabel(ax1, 'amplitud');
title(ax1, ['Señal original      x(t) = ' expr], 'Interpreter', 'none');

ax2 = axes('Parent', fig, 'Position', [0.09 0.520 0.87 0.205]);
plot(ax2, t, xt, '--', 'Color', [0.62 0.62 0.62], 'LineWidth', 1.5);
hold(ax2, 'on');
plot(ax2, t, yt, 'r', 'LineWidth', 2);
hold(ax2, 'off');
grid(ax2, 'on'); xlim(ax2, xl); ylim(ax2, yl);
xlabel(ax2, 't'); ylabel(ax2, 'amplitud');
title(ax2, ['Original (gris) vs transformada (roja)      ' formula], 'Interpreter', 'none');
legend(ax2, {'x(t)  original', formula}, 'Location', 'best');

annotation(fig, 'textbox', [0.045 0.035 0.915 0.395], ...
    'String', resumen, 'Tag', 'panel_resumen', ...
    'Interpreter', 'none', 'VerticalAlignment', 'top', ...
    'FontName', get(0, 'FixedWidthFontName'), 'FontSize', 9, ...
    'BackgroundColor', [0.97 0.97 0.97], 'EdgeColor', [0.75 0.75 0.75], ...
    'FitBoxToText', 'off', 'Margin', 8);
end


% =======================================================================
%  MODO INTERACTIVO
% =======================================================================
function modo_interactivo(x, expr)
S.x    = x;
S.expr = expr;
S.t    = linspace(-10, 10, 1500);
S.xt   = evaluar_senal(x, S.t);

m = max(abs(S.xt(isfinite(S.xt))));
if isempty(m) || m == 0 || ~isfinite(m)
    m = 1;
end
S.yl = [-(3*m + 2.2), (3*m + 2.2)];   % fijo: así SI se ve el cambio de amplitud

S.fig = figure('Name', 'Transformación de señales (interactivo)', ...
    'NumberTitle', 'off', 'Color', 'w', 'Position', [80 60 980 680]);
S.ax = axes('Parent', S.fig, 'Position', [0.08 0.56 0.89 0.37]);
S.info = uicontrol(S.fig, 'Style', 'text', 'Units', 'normalized', ...
    'Position', [0.06 0.285 0.90 0.20], 'HorizontalAlignment', 'left', ...
    'BackgroundColor', 'w', 'FontName', get(0, 'FixedWidthFontName'), 'FontSize', 9);

filas = {'A   amplitud'        -3  3  1
         'a   escala de tiempo' -3  3  1
         'b   corrimiento'      -5  5  0
         'B   nivel'            -2  2  0};
ys = [0.215 0.165 0.115 0.065];

for k = 1:4
    uicontrol(S.fig, 'Style', 'text', 'Units', 'normalized', ...
        'Position', [0.06 ys(k)-0.009 0.17 0.038], 'String', filas{k,1}, ...
        'HorizontalAlignment', 'left', 'BackgroundColor', 'w', 'FontSize', 9);
    S.sl(k) = uicontrol(S.fig, 'Style', 'slider', 'Units', 'normalized', ...
        'Position', [0.24 ys(k) 0.57 0.040], ...
        'Min', filas{k,2}, 'Max', filas{k,3}, 'Value', filas{k,4}, ...
        'SliderStep', [0.1 0.5] / (filas{k,3} - filas{k,2}));
    S.val(k) = uicontrol(S.fig, 'Style', 'text', 'Units', 'normalized', ...
        'Position', [0.83 ys(k)-0.009 0.12 0.038], 'String', '', ...
        'HorizontalAlignment', 'left', 'BackgroundColor', 'w', 'FontSize', 9);
end

uicontrol(S.fig, 'Style', 'pushbutton', 'Units', 'normalized', ...
    'Position', [0.06 0.012 0.17 0.042], 'String', 'Valores neutros', ...
    'Callback', @(varargin) reiniciar(S.fig));

guidata(S.fig, S);
for k = 1:4
    set(S.sl(k), 'Callback', @(varargin) actualizar(S.fig));
end
actualizar(S.fig);

fprintf('\n   Modo interactivo abierto: mueve los cuatro deslizadores.\n');
fprintf('   El titulo y el recuadro de abajo dicen que operacion estas haciendo.\n');
fprintf('   Cierra la ventana cuando termines.\n\n');
end


function actualizar(fig)
S = guidata(fig);

v = zeros(1, 4);
for k = 1:4
    v(k) = round(get(S.sl(k), 'Value') * 10) / 10;   % pasos de 0.1
end
if v(2) == 0
    v(2) = 0.1;                                       % a = 0 no vale
end
for k = 1:4
    set(S.sl(k), 'Value', v(k));
    set(S.val(k), 'String', n2s(v(k)));
end
A = v(1); a = v(2); b = v(3); B = v(4);

yt = A * evaluar_senal(S.x, a*S.t + b) + B;

cla(S.ax);
plot(S.ax, S.t, S.xt, '--', 'Color', [0.62 0.62 0.62], 'LineWidth', 1.5);
hold(S.ax, 'on');
plot(S.ax, S.t, yt, 'r', 'LineWidth', 2);
hold(S.ax, 'off');
grid(S.ax, 'on');
xlim(S.ax, [S.t(1) S.t(end)]);
ylim(S.ax, S.yl);
xlabel(S.ax, 't'); ylabel(S.ax, 'amplitud');
title(S.ax, formula_texto(A, a, b, B), 'Interpreter', 'none', 'FontSize', 12);
legend(S.ax, {'x(t)  original', 'y(t)  transformada'}, 'Location', 'northeast');

pasos = pasos_transformacion(A, a, b, B);
L = cell(numel(pasos) + 2, 1);
L{1} = sprintf('x(t) = %s        %s', S.expr, formula_texto(A, a, b, B));
L{2} = 'Operaciones, en orden:';
for k = 1:numel(pasos)
    L{k+2} = sprintf('   %d) %s', k, pasos{k});
end
set(S.info, 'String', L);
end


function reiniciar(fig)
S = guidata(fig);
neutros = [1 1 0 0];
for k = 1:4
    set(S.sl(k), 'Value', neutros(k));
end
actualizar(fig);
end


% =======================================================================
%  UTILIDADES
% =======================================================================
function s = n2s(v)
if v == 0
    v = 0;          % evita que salga "-0"
end
s = strtrim(num2str(v, '%.6g'));
end


function s = signo(v)
if v < 0
    s = '-';
else
    s = '+';
end
end


function imprimir_lineas(L)
fprintf('\n');
for k = 1:numel(L)
    fprintf('   %s\n', L{k});
end
end
