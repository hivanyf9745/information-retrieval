import { useSelector } from "react-redux";

const Pseudo = () => {
  console.log(JSON.parse(localStorage.getItem("searchedResults")));
  return (
    <div>
      <h1>This is the pseudo relevance page</h1>
    </div>
  );
};

export default Pseudo;
