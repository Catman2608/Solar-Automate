def _collect_block_body(self, actions, i, end):
        """
        Reads lines until the matching closing brace or until a keyword
        that terminates the block (else / endif).
        Returns (body_lines, new_i).

        Supports both brace-delimited  { … }  and brace-less (one-liners).
        """
        if i < end and actions[i].strip() == "{":
            i += 1  # skip standalone opening brace

        depth = 0
        body_lines = []
        while i < end:
            stripped = actions[i].strip()

            if stripped == "{":
                depth += 1
                body_lines.append(stripped)  # keep inner braces for nested blocks
                i += 1
                continue

            if stripped.startswith("}"):
                if depth == 0:
                    if stripped == "}":
                        i += 1
                    break
                depth -= 1
                body_lines.append(stripped)  # keep inner braces for nested blocks
                i += 1
                continue

            lower = stripped.lower()
            if depth == 0 and (lower == "else" or lower.startswith("else ") or lower == "endif" or lower.startswith("endif ")):
                break

            body_lines.append(stripped)
            i += 1

        return body_lines, i
