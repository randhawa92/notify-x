import "../styles/Features.css";

function Features() {
  return (
    <section className="features">

      <div className="section-title">
        <h2>Powerful Features</h2>
        <p>
          Everything you need to automate communication using AI.
        </p>
      </div>

      <div className="feature-grid">

        <div className="feature-card">
          <div className="icon">🤖</div>
          <h3>AI Message Generation</h3>
          <p>
            Generate personalized messages automatically using AI.
          </p>
        </div>

        <div className="feature-card">
          <div className="icon">📊</div>
          <h3>Excel Processing</h3>
          <p>
            Upload Excel files and process thousands of records instantly.
          </p>
        </div>

        <div className="feature-card">
          <div className="icon">💬</div>
          <h3>WhatsApp Automation</h3>
          <p>
            Send messages automatically through WhatsApp Web.
          </p>
        </div>

      </div>

    </section>
  );
}

export default Features;