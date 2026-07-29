// src/components/ui/Field.jsx
export function Field({ label, hint, children }) {
  return (
    <label className="field-group">
      <span className="field-label">{label}</span>
      {children}
      {hint && <span className="field-hint">{hint}</span>}
    </label>
  );
}