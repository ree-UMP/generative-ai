# jac_llm_calculator.py
# A Jac + Typed LLM inspired calculator — single Python file version

# --- Mock Typed LLM class (safe for local use) ---
# If you have BYLLM installed, you can replace this mock with:
# from byllm import TypedLLM
class TypedLLM:
    def typed(self, func):
        # Acts as a decorator — just returns the original function
        return func


# Initialize "LLM"
llm = TypedLLM()

# --- Define a typed LLM computation function ---
@llm.typed
def calculate(expr: str) -> float:
    """
    Evaluates simple math expressions (e.g. '2 + 3 * 4').
    Safe subset only — blocks unsafe code.
    """
    import re, math

    # Allow only numbers, + - * / ( ) . and spaces
    if not re.match(r"^[0-9\.\+\-\*\/\(\) ]+$", expr):
        return "Invalid: only numbers and + - * / ( ) allowed"

    try:
        # Evaluate safely
        result = eval(expr, {"__builtins__": None}, {"math": math})
        return round(float(result), 5)
    except Exception:
        return "Error: invalid expression"


# --- Simulated Jac walker flow ---
def jac_walker():
    print("╔════════════════════════════════════════╗")
    print("║   Welcome to Jac + Typed LLM Calculator ║")
    print("╚════════════════════════════════════════╝")

    while True:
        expr = input("\nEnter expression (or 'exit' to quit): ").strip()

        if expr.lower() == "exit":
            print("Goodbye 👋")
            break

        if not expr:
            print("Please type something.")
            continue

        # Jac 'emit' → send to LLM
        result = calculate(expr)

        print(f"→ Result: {result}")


# --- Run the Jac-inspired app ---
if __name__ == "__main__":
    jac_walker()





