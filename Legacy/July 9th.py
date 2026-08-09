def _handle_assignment(self, action):
    """
    Split the value and the target variables, then update the value based on the target variable.
    Handles: SettingsFile := A_ScriptDir . "\\Configs\\" . ActiveConfig . ".ini"
    """
    if ":=" in action:
        var, value = action.split(":=", 1)
        var = var.strip()
        value = value.strip()
        
        # Prevent overwriting built-ins
        if var in self.builtin_variables:
            messagebox.showerror("Error", f"Cannot overwrite built-in variable: {var}")
            raise NameError(f"Cannot overwrite built-in variable: '{var}'")

        expr = value
        
        # 1. Normalize AHK string concatenation (. ) -> Python (+)
        expr = re.sub(r"\s+\.\s+", " + ", expr)
        
        # 2. Safely escape literal backslashes inside AHK double quotes 
        # so Python eval doesn't see them as malicious escapes (e.g., \C or \")
        def escape_string(match):
            text = match.group(0)
            # Retain outer quotes, replace raw single backslashes with double backslashes
            inner_content = text[1:-1].replace("\\", "\\\\")
            return f'"{inner_content}"'
            
        expr = re.sub(r'"[^"]*"', escape_string, expr)

        try:
            # Eval namespace will accurately substitute A_ScriptDir and ActiveConfig
            self.variables[var] = eval(expr, {}, self._get_eval_namespace())
        except Exception as e:
            messagebox.showerror("Syntax Error", f"Failed to evaluate assignment: {action}\n{e}")
            raise e
            
        return True
    return False