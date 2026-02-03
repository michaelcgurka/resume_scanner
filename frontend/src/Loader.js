import React from "react";
import { ThreeDots } from "react-loader-spinner";
import { useTheme } from "./ThemeContext";

function Loader({ color }) {
    const { theme } = useTheme();
    const spinnerColor = color ?? (theme === "dark" ? "#9ca3af" : "#6b7280");

    return (
        <ThreeDots
            visible={true}
            height="80"
            width="80"
            color={spinnerColor}
            radius="9"
            ariaLabel="three-dots-loading"
            wrapperStyle={{}}
            wrapperClass=""
        />
    );
}

export default Loader;
