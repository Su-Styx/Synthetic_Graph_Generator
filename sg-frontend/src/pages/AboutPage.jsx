import bgImage from "../assets/bcg.png";

export default function AboutPage() {
    <h1> You've reached the About Page</h1>
return (
    <div
          style={{
            minHeight: "100vh",
            width: "100vw",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            position: "relative",
            backgroundImage: `url(${bgImage})`,
            backgroundSize: "cover",
            backgroundPosition: "center",
            backgroundRepeat: "no-repeat",
          }}
        >
            <h1> You've reached the About Page</h1>
        </div>
)}