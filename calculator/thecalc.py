class TypedLLM:
    def typed(self, func):
        
        return func



llm = TypedLLM()


@llm.typed
def calculate(expr: str) -> float:
    """
    Evaluates simple math expressions (e.g. '2 + 3 * 4').
    Safe subset only — blocks unsafe code.
    """
    import re, math

    if not re.match(r"^[0-9\.\+\-\*\/\(\) ]+$", expr):
        return "Invalid: only numbers and + - * / ( ) allowed"

    try:
        
        result = eval(expr, {"__builtins__": None}, {"math": math})
        return round(float(result), 5)
    except Exception:
        return "Error: invalid expression"


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

      
        result = calculate(expr)

        print(f"→ Result: {result}")



if __name__ == "__main__":
    jac_walker()





