export function Panel({ title, accent, action, children }) {
  return (
    <section className={`panel ${accent ? "accent" : ""}`}>
      {title && (
        <div className="panel-header">
          <h3 className={`panel-title ${accent ? "error" : ""}`}>{title}</h3>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}