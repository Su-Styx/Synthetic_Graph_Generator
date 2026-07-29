import bgImage from "../assets/bcg.png";

export default function SettingsPage() {
const username = localStorage.getItem("username") || "Unknown user";

return( 
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
          }}>
    <h1>
        Welcome {username} 
    </h1>
    <h2>
        You have reached the Settings page 
    </h2>
    </div>

)

}

