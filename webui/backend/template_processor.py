"""
Template Processor for Kometa Web UI

Simplified template processing for overlay preview.
This handles the most common template patterns used in Kometa overlay files
without the full complexity of the main Kometa template engine.
"""

import re
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from ruamel.yaml import YAML


class TemplateProcessor:
    """Processes Kometa templates for overlay preview."""

    def __init__(self, kometa_root: Path):
        self.kometa_root = Path(kometa_root)
        self.defaults_dir = self.kometa_root / "defaults" / "overlays"
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self._template_cache: Dict[str, Dict] = {}

    def load_templates(self, template_source: str = "templates") -> Dict[str, Any]:
        """Load templates from a template file."""
        if template_source in self._template_cache:
            return self._template_cache[template_source]

        # Handle 'default: templates' which refers to templates.yml in the same directory
        if template_source == "templates":
            template_path = self.defaults_dir / "templates.yml"
        else:
            template_path = Path(template_source)
            if not template_path.is_absolute():
                template_path = self.defaults_dir / template_source

        if not template_path.exists():
            return {}

        try:
            with open(template_path, encoding="utf-8") as f:
                data = self.yaml.load(f)
            templates = data.get("templates", {}) if data else {}
            self._template_cache[template_source] = templates
            return templates
        except Exception as e:
            print(f"Failed to load templates from {template_path}: {e}")
            return {}

    def resolve_variable(self, value: Any, variables: Dict[str, Any]) -> Any:
        """Resolve <<variable>> placeholders in a value."""
        if value is None:
            return None

        if isinstance(value, str):
            # Handle simple variable substitution
            result = value
            for var_name, var_value in variables.items():
                placeholder = f"<<{var_name}>>"
                if placeholder in result:
                    if result == placeholder:
                        # Entire value is the variable
                        return var_value
                    else:
                        # Variable is part of a larger string
                        result = result.replace(placeholder, str(var_value) if var_value is not None else "")

            # Handle nested variable references like <<key>> where key itself has a value
            pattern = r'<<([^>]+)>>'
            matches = re.findall(pattern, result)
            for match in matches:
                if match in variables and variables[match] is not None:
                    result = result.replace(f"<<{match}>>", str(variables[match]))

            return result

        elif isinstance(value, dict):
            return {k: self.resolve_variable(v, variables) for k, v in value.items()}

        elif isinstance(value, list):
            return [self.resolve_variable(item, variables) for item in value]

        return value

    def evaluate_conditionals(
        self,
        conditionals: Dict[str, Any],
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate conditional expressions and return resolved values."""
        results = {}

        for cond_name, cond_def in conditionals.items():
            if not isinstance(cond_def, dict):
                continue

            default_value = cond_def.get("default")
            conditions = cond_def.get("conditions", [])

            if isinstance(conditions, dict):
                conditions = [conditions]

            resolved_value = default_value
            for condition in conditions:
                if not isinstance(condition, dict):
                    continue

                condition_value = condition.get("value")
                condition_met = True

                for check_key, check_value in condition.items():
                    if check_key == "value":
                        continue

                    # Handle .exists checks
                    if check_key.endswith(".exists"):
                        var_name = check_key[:-7]
                        var_exists = var_name in variables and variables[var_name] is not None
                        expected = check_value if isinstance(check_value, bool) else str(check_value).lower() == "true"
                        if var_exists != expected:
                            condition_met = False
                            break

                    # Handle .not checks
                    elif check_key.endswith(".not"):
                        var_name = check_key[:-4]
                        if var_name in variables:
                            var_val = variables[var_name]
                            if isinstance(check_value, list):
                                if var_val in check_value:
                                    condition_met = False
                                    break
                            elif str(var_val) == str(check_value):
                                condition_met = False
                                break

                    # Standard equality check
                    elif check_key in variables:
                        var_val = variables[check_key]
                        if isinstance(check_value, list):
                            if var_val not in check_value:
                                condition_met = False
                                break
                        elif str(var_val) != str(check_value):
                            condition_met = False
                            break
                    else:
                        # Variable doesn't exist, condition fails
                        condition_met = False
                        break

                if condition_met:
                    resolved_value = condition_value
                    break

            # Resolve any variables in the result
            results[cond_name] = self.resolve_variable(resolved_value, variables)

        return results

    def process_template(
        self,
        template_name: str,
        template_def: Dict[str, Any],
        user_variables: Dict[str, Any],
        key: str = ""
    ) -> Dict[str, Any]:
        """Process a single template with user-provided variables."""
        # Start with default variables
        variables = {}

        # Add 'key' variable which is commonly used
        variables["key"] = key

        # Process template defaults
        if "default" in template_def and isinstance(template_def["default"], dict):
            for dk, dv in template_def["default"].items():
                resolved_key = self.resolve_variable(dk, variables)
                resolved_value = self.resolve_variable(dv, variables)
                variables[resolved_key] = resolved_value

        # Apply user variables (these override defaults)
        for uk, uv in user_variables.items():
            variables[uk] = uv

        # Process conditionals
        if "conditionals" in template_def and isinstance(template_def["conditionals"], dict):
            conditional_results = self.evaluate_conditionals(template_def["conditionals"], variables)
            variables.update(conditional_results)

        # Now resolve the overlay configuration
        overlay_def = template_def.get("overlay", {})
        if not overlay_def:
            return {}

        resolved_overlay = {}
        for ok, ov in overlay_def.items():
            resolved_key = self.resolve_variable(ok, variables)
            resolved_value = self.resolve_variable(ov, variables)
            # Skip if value is still an unresolved variable or None
            if resolved_value is not None and not (isinstance(resolved_value, str) and "<<" in resolved_value):
                resolved_overlay[resolved_key] = resolved_value

        return resolved_overlay

    def expand_overlay_file(
        self,
        file_path: str,
        user_template_variables: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Expand an overlay file, processing all templates and returning
        a list of fully resolved overlay configurations.
        """
        path = Path(file_path)
        if not path.exists():
            return []

        try:
            with open(path, encoding="utf-8") as f:
                data = self.yaml.load(f)
        except Exception as e:
            print(f"Failed to load overlay file {file_path}: {e}")
            return []

        if not data:
            return []

        user_vars = user_template_variables or {}
        expanded_overlays = []

        # Load external templates if specified
        external_templates = {}
        if "external_templates" in data:
            ext_tmpl = data["external_templates"]
            if isinstance(ext_tmpl, dict):
                template_source = ext_tmpl.get("default", "templates")
                external_templates = self.load_templates(template_source)

                # Also pick up any template_variables from external_templates
                if "template_variables" in ext_tmpl and isinstance(ext_tmpl["template_variables"], dict):
                    for tk, tv in ext_tmpl["template_variables"].items():
                        if tk not in user_vars:
                            user_vars[tk] = tv

        # Load local templates
        local_templates = data.get("templates", {})

        # Combine templates (local takes precedence)
        all_templates = {**external_templates, **local_templates}

        # Process each overlay
        overlays_section = data.get("overlays", {})
        for overlay_name, overlay_def in overlays_section.items():
            if not isinstance(overlay_def, dict):
                continue

            # Check if this overlay uses a template
            if "template" in overlay_def:
                template_call = overlay_def["template"]
                template_calls = template_call if isinstance(template_call, list) else [template_call]

                for tmpl_call in template_calls:
                    if isinstance(tmpl_call, dict):
                        tmpl_name = tmpl_call.get("name", "standard")
                        tmpl_vars = {k: v for k, v in tmpl_call.items() if k != "name"}
                    elif isinstance(tmpl_call, str):
                        tmpl_name = tmpl_call
                        tmpl_vars = {}
                    else:
                        continue

                    if tmpl_name not in all_templates:
                        continue

                    template_def = all_templates[tmpl_name]
                    if isinstance(template_def, list) and len(template_def) > 0:
                        template_def = template_def[0]

                    # Combine variables: user_vars + template call vars + overlay-specific
                    combined_vars = {**user_vars, **tmpl_vars}
                    if "template_variables" in overlay_def:
                        combined_vars.update(overlay_def["template_variables"])

                    # Extract key from overlay name for variable substitution
                    key = overlay_name.split("-")[-1] if "-" in overlay_name else overlay_name

                    resolved = self.process_template(tmpl_name, template_def, combined_vars, key)
                    if resolved:
                        resolved["_original_name"] = overlay_name
                        resolved["_template"] = tmpl_name
                        expanded_overlays.append(resolved)

            # Direct overlay definition (no template)
            elif "overlay" in overlay_def:
                overlay_config = overlay_def["overlay"]
                if isinstance(overlay_config, dict):
                    # Resolve any variables in the direct definition
                    resolved = {}
                    for ok, ov in overlay_config.items():
                        resolved_value = self.resolve_variable(ov, user_vars)
                        if resolved_value is not None:
                            resolved[ok] = resolved_value

                    resolved["_original_name"] = overlay_name
                    resolved["_direct"] = True
                    expanded_overlays.append(resolved)

        return expanded_overlays

    def get_overlay_keys_from_file(self, file_path: str) -> List[str]:
        """Get all overlay keys/names from a file without full expansion."""
        path = Path(file_path)
        if not path.exists():
            return []

        try:
            with open(path, encoding="utf-8") as f:
                data = self.yaml.load(f)
        except Exception:
            return []

        if not data or "overlays" not in data:
            return []

        return list(data["overlays"].keys())
