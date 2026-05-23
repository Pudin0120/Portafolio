package simplejavacalculator;

import static java.lang.Double.NaN;
import static java.lang.Math.log10;
import static java.lang.Math.pow;

/**
 * Calculator class that handles basic and advanced mathematical operations.
 * Mejorada con estructuras switch y validaciones de seguridad.
 */
public class Calculator {

    /**
     * Modes for operations that require two numbers (binary operations).
     */
    public enum BiOperatorModes {
        normal, add, minus, multiply, divide, xpowerofy 
    }

    /**
     * Modes for operations that require one number (unary operations).
     */
    public enum MonoOperatorModes {
        square, squareRoot, oneDividedBy, cos, sin, tan, log, rate, abs
    }

    private double num1, num2;
    private BiOperatorModes mode = BiOperatorModes.normal;

    /**
     * Internal implementation of binary calculations using switch for clarity.
     * @return The result of the operation applied to num1 and num2.
     */
    private double calculateBiImpl() {
        switch (mode) {
            case add:
                return num1 + num2;
            case minus:
                return num1 - num2;
            case multiply:
                return num1 * num2;
            case divide:
                // Validation to avoid division by zero
                return (num2 != 0) ? num1 / num2 : NaN;
            case xpowerofy:
                return pow(num1, num2);
            case normal:
                return num2;
            default:
                throw new UnsupportedOperationException("Unsupported operation mode");
        }
    }

    /**
     * Prepares and executes a binary calculation.
     * @param newMode The new operation mode to set.
     * @param num The current entered number.
     * @return El resultado acumulado o NaN si es la primera entrada.
     */
    public Double calculateBi(BiOperatorModes newMode, Double num) {
        if (mode == BiOperatorModes.normal) {
            num2 = 0.0;
            num1 = num;
            mode = newMode;
            return NaN;
        } else {
            num2 = num;
            num1 = calculateBiImpl();
            mode = newMode;
            return num1;
        }
    }

    /**
     * Executes the final calculation (equals button).
     */
    public Double calculateEqual(Double num) {
        return calculateBi(BiOperatorModes.normal, num);
    }

    /**
     * Reinicia los valores de la calculadora.
     */
    public Double reset() {
        num2 = 0.0;
        num1 = 0.0;
        mode = BiOperatorModes.normal;
        return NaN;
    }

    /**
     * Performs single-operand operations with mathematical validations.
     * @param newMode Operation to perform.
     * @param num Number to operate on.
     * @return Calculation result.
     */
    public Double calculateMono(MonoOperatorModes newMode, Double num) {
        switch (newMode) {
            case square:
                return num * num;
            case squareRoot:
                return (num >= 0) ? Math.sqrt(num) : NaN;
            case oneDividedBy:
                return (num != 0) ? 1 / num : NaN;
            case cos:
                return Math.cos(Math.toRadians(num));
            case sin:
                return Math.sin(Math.toRadians(num));
            case tan:
                // Tangent asymptote handling
                if (num % 180 == 0) return 0.0;
                if (num % 90 == 0 && num % 180 != 0) return NaN;
                return Math.tan(Math.toRadians(num));
            case log:
                return (num > 0) ? log10(num) : NaN;
            case rate:
                return num / 100;
            case abs:
                return Math.abs(num);
            default:
                return NaN;
        }
    }
}
