from math import sin, cos, pi


class Fractal:
    def __init__(self, iterations, axiom, rules, angle,
                 correction_angle=0, offset=None, width=450, height=450, zoom=1):

        if offset is None:
            self.offset = [0, 0]
        else:
            self.offset = offset.copy()

        instructions = self.create_instructions(iterations, axiom, rules)
        min_x, min_y, max_x, max_y = self.calc_offset(instructions, angle, correction_angle)

        width_ = abs(min_x) + abs(max_x)
        height_ = abs(min_y) + abs(max_y)

        if width_ == 0 or height_ == 0:
            self.points = []
            return

        margin = 35
        if width_ > height_:
            length = (width - 2 * margin) / width_
        else:
            length = (height - 2 * margin) / height_
        length *= zoom

        self.offset[0] *= zoom
        self.offset[1] *= zoom

        self.offset[0] += abs(min_x * length)
        self.offset[1] += abs(min_y * length)

        width = round(width_ * length)
        height = round(height_ * length)

        points = self.generate_points(instructions, length, angle, correction_angle)

        self.width = width + 1
        self.height = height + 1
        self.points = points

    @staticmethod
    def calc_offset(instructions, angle, correction_angle) -> tuple:
        current_angle = correction_angle
        length = 1
        min_x, min_y = 0, 0
        max_x, max_y = 0, 0
        point = (0, 0)
        saved_points = []
        for i in instructions:
            if i == "+":
                current_angle -= angle
            elif i == "-":
                current_angle += angle
            elif i == "[":
                saved_points.append([point, current_angle])
            elif i == "]":
                point, current_angle = saved_points[-1]
                saved_points = saved_points[:-1]
            elif i in "Ff":
                x = point[0] + cos(current_angle * pi / 180) * length
                y = point[1] + sin(current_angle * pi / 180) * length
                point = (x, y)
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
        return min_x, min_y, max_x, max_y

    @staticmethod
    def create_instructions(iterations, axiom, rules) -> str:
        for _ in range(iterations):
            res = ""
            for i in axiom:
                if i in rules:
                    res += rules[i]
                else:
                    res += i
            if ">" in res:
                res += "<"
            axiom = res
        return axiom

    @staticmethod
    def generate_points(instructions, length, angle, correction_angle) -> list:
        points = []
        current_angle = correction_angle
        point = (0, 0, True)
        saved_points = []
        for i in instructions:
            if i == "+":
                current_angle -= angle
            elif i == "-":
                current_angle += angle
            elif i == "[":
                saved_points.append(((point[0], point[1], False), current_angle))
            elif i == "]":
                points.append(point)
                point, current_angle = saved_points[-1]
                saved_points = saved_points[:-1]
            elif i == "F":
                points.append(point)
                x = point[0] + cos(current_angle * pi / 180) * length
                y = point[1] + sin(current_angle * pi / 180) * length
                point = (x, y, True)
            elif i == "f":
                points.append(point)
                x = point[0] + cos(current_angle * pi / 180) * length
                y = point[1] + sin(current_angle * pi / 180) * length
                point = (x, y, False)
        points.append(point)
        return points
