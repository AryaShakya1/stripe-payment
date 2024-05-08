import "./App.css";
import Payment from "./components/Payment";
import { Elements } from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";

var apiKey = import.meta.env.VITE_API_KEY;
const stripePromise = await loadStripe(apiKey);

function App() {
  const options = {
    mode: "payment",
    amount: 2000,
    currency: "usd",
  };
  return (
    <>
      <Elements stripe={stripePromise} options={options}>
        <Payment />
      </Elements>
    </>
  );
}

export default App;


