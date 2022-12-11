import { Outlet } from "react-router-dom";
import "./navigation.styles.scss";

const Navigation = () => {
  return (
    <div>
      <div className='header-img' />
      <Outlet />
    </div>
  );
};

export default Navigation;
