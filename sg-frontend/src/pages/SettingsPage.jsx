export default function SettingsPage() {
const username = localStorage.getItem("username") || "Unknown user";

return( 
    <div>
    <h1>
        Welcome {username} 
    </h1>
    <h2>
        You have reached the Settings page 
    </h2>
    </div>

)

}