
# Autor: Marius Montebaur
# Datum: 22.02.18

# Modul zur Berechnung von Interpolationsfunktionen
# Liste von Punkten kann uebergeben werden
# Interpolationsgeraden 1. oder 3. Grades werden zwischen diesen
# Punkten berechnet.
# Dabei ist ein "zyklischer Aufbau" gewaehrleistet:
#   Der erste und letzte Wert sind auch durch ein Polynom miteinander
#   verbunden. Siehe python_interpolation.pdf

# Berechnung der Interpolationsterme:
#   Siehe Scans und ausserdem mit Hilfe von Wolfram Alpha
#   Inverse bei WA: inv{{v^3, v^2, v, 1},{w^3, w^2, w, 1},{3v^2, 2v, 1, 0},{3w^2, 2w, 1, 0}}
#   Ergibt mit Vektor (y_1, y_2, 0, 0)^T multipliziert die Ergebnisse
#   von Vektor (a, b, c, d)


def float_range(start, end, step):
    i = start
    ret = []
    while i < end:
        ret.append(i)
        i += step
    return ret


def scilab_str(array, precision=2):
    sce_str = "["
    for i in array:
        sce_str += str(round(i,precision))
        sce_str += " "

    sce_str = sce_str[:-1]
    sce_str += "]"
    return sce_str


class InterpolatedFunction:

    # Stellt ein einzelnes Interpolationspolynom von 1. oder 3. Grad dar
    class PolynomialFromPoints:
        # start und end sind Tupel aus x und y Koordinate
        def __init__(self, start, end, degree=1):
            self.degree = degree
            x_1 = start[0]
            y_1 = start[1]
            x_2 = end[0]
            y_2 = end[1]
            self.start = x_1
            self.end = x_2
            if self.degree == 1:
                # berechnet die Koeffizienten fuer ein Interpolationspolynom
                # 1. Grades
                self.m = (y_2 - y_1)/(x_2 - x_1)
                self.b = y_1 - (self.m * x_1)

            elif self.degree == 3:
                # berechnet die Koeffizienten fuer ein Interpolationspolynom
                # 3. Grades unter der Annahme, dass die Steigung in den
                # gegebenen Punkten gleich Null ist.
                self.a = (2*(y_2 - y_1))/((x_1 - x_2)**3)
                self.b = (3*(x_1 + x_2)*(y_1 - y_2))/((x_1 - x_2)**3)
                self.c = (6*x_1*x_2*(y_2 - y_1))/((x_1 - x_2)**3)
                d_zaehler = y_1*(3*x_1*x_2**2 - x_2**3) + y_2*(x_1**3 - 3*x_2*x_1**2)
                self.d = (d_zaehler)/((x_1 - x_2)**3)
            else:
                print("Bitte Grad 1 oder 3 waehlen")

        def value(self, x):
            if x < self.start or x > self.end or (self.degree != 1 and self.degree != 3):
                return -1

            if self.degree == 3:
                y = self.a*x**3 + self.b*x**2 + self.c*x + self.d
                return y

            if self.degree == 1:
                return self.m * x + self.b

        # Geben Definitionsbereich zurueck
        def domain_start(self):
            return self.start

        def domain_end(self):
            return self.end
    # Ende der Darstellung eines Interpolationspolynoms

    # Liste von (x, y)-Tupeln und ein maximaler x-Wert
    def __init__(self, points_list, x_max, degree=1):
        self.degree = degree
        self.points_list = points_list
        self.x_max = x_max
        if not self.points_list:
            # Standardwert setzen
            self.points_list = [(0, 8)]
        self.points_list.sort()
        self.init_interpolation()

    def init_interpolation(self):
        self.inter_list = []

        # zuerst fuer erstes Elemnt
        start = (-(self.x_max - self.points_list[-1][0]), self.points_list[-1][1])
        end = self.points_list[0]
        ipol = self.PolynomialFromPoints(start, end, self.degree)
        self.inter_list.append(ipol)

        # -1 hier sinnvoll, weil letztes Element ein Sonderfall
        for i in range(len(self.points_list)-1):
            start = self.points_list[i]
            end = self.points_list[i+1]
            ipol = self.PolynomialFromPoints(start, end, self.degree)
            self.inter_list.append(ipol)

        # dann fuer letztes Element:
        start = (self.points_list[-1])
        end = (self.points_list[0][0] + self.x_max, self.points_list[0][1])
        ipol = self.PolynomialFromPoints(start, end, self.degree)
        self.inter_list.append(ipol)

    def value(self, x):
        if x > self.x_max or x < 0:
            return -1

        for i in range(len(self.inter_list)-1):
            if self.inter_list[i+1].domain_start() > x:
                return self.inter_list[i].value(x)

        return self.inter_list[-1].value(x)


# Liste mit Zeiten und Werten ab dann:
# [(0, 6), (9, 4)]
# -> Ab 0 Uhr: 6
# -> Ab 9 Uhr: 4

def main():
    print("Ausgabe von Funktionswerten, die gegebene Punkte ein mal mit")
    print("  Polynomen 1. und ein mal mit Polynomen 3. Grades interpolieren.")
    print("  Ausserdem Ausgabeformat zum Kopieren in Scilab.")

    points = [(3, 1), (7, 5.5), (12.5, 3), (14, 3), (16, 1), (18, 1), (21, 2)]
    poly_deg1 = InterpolatedFunction(points, 24, 1)
    poly_deg3 = InterpolatedFunction(points, 24, 3)
    values_x = []
    values_y1 = []
    values_y3 = []

    for i in float_range(0, 24, 0.2):
        y_1 = poly_deg1.value(i)
        y_3 = poly_deg3.value(i)

        values_x.append(i)
        values_y1.append(y_1)
        values_y3.append(y_3)

    print("x =", scilab_str(values_x))
    print("y_1 =", scilab_str(values_y1, 4))
    print("y_3 =", scilab_str(values_y3, 4))


if __name__ == "__main__":
    main()
