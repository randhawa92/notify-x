import "../styles/Status.css";

function Status() {
  return (
    <section className="status-section">

      <div className="status-title">
        <h2>How It Works</h2>
        <p>
          Upload → AI Generate → WhatsApp Send
        </p>
      </div>

      <div className="status-container">

        <div className="status-card">
          <div className="status-number">01</div>
          <h3>Upload Excel</h3>
          <p>
            Upload student or customer data in Excel format.
          </p>
        </div>

        <div className="status-card">
          <div className="status-number">02</div>
          <h3>AI Generates Messages</h3>
          <p>
            AI creates personalized messages automatically.
          </p>
        </div>

        <div className="status-card">
          <div className="status-number">03</div>
          <h3>Send on WhatsApp</h3>
          <p>
            Bulk messages are delivered through WhatsApp.
          </p>
        </div>

      </div>

    </section>
  );
}

export default Status;