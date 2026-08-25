export function Toggle({ checked, onChange, on = "On", off = "Off" }) {
  return (
    <button type="button" className="toggle" onClick={onChange}>
      {checked ? on : off}
      <span className={`toggle-track ${checked ? "on" : ""}`}>
        <span className={`toggle-thumb ${checked ? "on" : ""}`} />
      </span>
    </button>
  );
}