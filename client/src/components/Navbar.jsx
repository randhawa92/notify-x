import "../styles/Navbar.css";

function Navbar() {
  return (
    <nav className="navbar">
      <div className="logo">
        NOTIFY<span>X</span>
      </div>

      <ul className="nav-links">
        <li>Home</li>
        <li>Features</li>
        <li>AI Engine</li>
        <li>Contact</li>
      </ul>

      <button className="nav-btn">
        Sign In
      </button>
    </nav>
  );
}

export default Navbar;