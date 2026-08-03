import { Field } from "../Field";
import { emptyRule } from "./AttributeRules";

export default function AttributeEditor({ label, rules, setRules }) {
  const addRule = () => setRules((prev) => [...prev, emptyRule()]);
  const removeRule = (id) => setRules((prev) => prev.filter((r) => r.id !== id));
  const updateRule = (id, patch) =>
    setRules((prev) => prev.map((r) => (r.id === id ? { ...r, ...patch } : r)));

  return (
    <div className="attr-section">
      <div className="attr-section-header">
        <p className="attr-section-title">{label}</p>
        <button type="button" className="attr-add-btn" onClick={addRule}>
          + Add attribute
        </button>
      </div>

      {!rules.length && (
        <p className="attr-empty-note">No {label.toLowerCase()} configured.</p>
      )}

      {rules.map((rule) => (
        <AttributeRuleRow
          key={rule.id}
          rule={rule}
          onChange={(patch) => updateRule(rule.id, patch)}
          onRemove={() => removeRule(rule.id)}
        />
      ))}
    </div>
  );
}

function AttributeRuleRow({ rule, onChange, onRemove }) {
  return (
    <div className="attr-rule-row">
      <div className="attr-rule-top">
        <input
          className="field-input attr-name-input"
          placeholder="Attribute name"
          value={rule.name}
          onChange={(e) => onChange({ name: e.target.value })}
        />

        <select
          className="field-select attr-kind-select"
          value={rule.kind}
          onChange={(e) => onChange({ kind: e.target.value })}
        >
          <option value="categorical">Categorical</option>
          <option value="numeric">Numeric</option>
          <option value="timestamp">Timestamp</option>
        </select>

        <button type="button" className="attr-remove-btn" onClick={onRemove}>
          ✕
        </button>
      </div>

      {rule.kind === "categorical" && (
        <div className="attr-rule-fields">
          <Field label="Values">
            <input
              className="field-input"
              value={rule.values}
              onChange={(e) => onChange({ values: e.target.value })}
              placeholder="admin,user,guest"
            />
          </Field>
          <Field label="Weights (optional)">
            <input
              className="field-input"
              value={rule.weights}
              onChange={(e) => onChange({ weights: e.target.value })}
              placeholder="0.1,0.7,0.2"
            />
          </Field>
        </div>
      )}

      {rule.kind === "numeric" && (
        <div className="attr-rule-fields">
          <Field label="Distribution">
            <select
              className="field-select"
              value={rule.distribution}
              onChange={(e) => onChange({ distribution: e.target.value })}
            >
              <option value="uniform">Uniform</option>
              <option value="normal">Normal</option>
            </select>
          </Field>

          {rule.distribution === "uniform" ? (
            <>
              <Field label="Min">
                <input
                  className="field-input"
                  type="number"
                  value={rule.min}
                  onChange={(e) => onChange({ min: e.target.value })}
                />
              </Field>
              <Field label="Max">
                <input
                  className="field-input"
                  type="number"
                  value={rule.max}
                  onChange={(e) => onChange({ max: e.target.value })}
                />
              </Field>
            </>
          ) : (
            <>
              <Field label="Mean">
                <input
                  className="field-input"
                  type="number"
                  value={rule.mean}
                  onChange={(e) => onChange({ mean: e.target.value })}
                />
              </Field>
              <Field label="Std deviation">
                <input
                  className="field-input"
                  type="number"
                  value={rule.std}
                  onChange={(e) => onChange({ std: e.target.value })}
                />
              </Field>
            </>
          )}
        </div>
      )}

      {rule.kind === "timestamp" && (
        <div className="attr-rule-fields">
          <Field label="Start date">
            <input
              className="field-input"
              type="date"
              value={rule.start}
              onChange={(e) => onChange({ start: e.target.value })}
            />
          </Field>
          <Field label="End date">
            <input
              className="field-input"
              type="date"
              value={rule.end}
              onChange={(e) => onChange({ end: e.target.value })}
            />
          </Field>
        </div>
      )}
    </div>
  );
}