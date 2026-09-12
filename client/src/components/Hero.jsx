import "../styles/Hero.css";

function Hero() {
  return (
    <section className="hero">
      <div className="hero-content">

        <span className="hero-badge">
          🚀 AI Powered Communication Platform
        </span>

        <h1>
          AI Powered WhatsApp
          <br />
          Notification Platform
        </h1>

        <p>
          Upload Excel files, generate personalized messages using AI,
          and send bulk WhatsApp notifications automatically in just a
          few clicks.
        </p>

        <div className="hero-buttons">
          <button className="primary-btn">
            Generate Messages
          </button>
        </div>

      </div>
    </section>
  );
}

export default Hero;