// src/components/ui/Panel.jsx
export function Panel({ title, accent, action, children }) {
  return (
    <section className={`panel ${accent ? "accent" : ""}`}style={{backgroundColor: "rgba(239, 248, 250, 0.22)"}}>
      {title && (
        <div className="panel-header">
          <h3 style={{fontWeight:"bold",fontSize:"22pt"}}className={`panel-title ${accent ? "error" : ""}`}>{title}</h3>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}