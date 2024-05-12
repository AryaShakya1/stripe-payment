import { useState } from "react";
import {
  PaymentElement,
  useStripe,
  useElements,
} from "@stripe/react-stripe-js";

function Payment() {
  const stripe = useStripe();
  const elements = useElements();
  const min_amount = 0.5;
  const max_amount = 999999.99;
  const [errorMessage, setErrorMessage] = useState(null);
  const [amount, setAmount] = useState(0);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (elements == null) {
      return;
    }

    // Trigger form validation and wallet collection
    const { error: submitError } = await elements.submit();
    if (submitError) {
      // Show error to your customer
      setErrorMessage(submitError.message);
      return;
    }

    if (amount < min_amount) {
      setErrorMessage(`The amount should be greater than ${min_amount}`);
      return;
    }
    if (amount > max_amount) {
      setErrorMessage(`The amount should be less than ${max_amount}`);
      return;
    }
    // Create the PaymentIntent and obtain clientSecret from your server endpoint
    const res = await fetch("http://localhost:8000/payment/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ amount: amount * 100 }),
    });

    const { client_secret: clientSecret } = await res.json();

    const { error } = await stripe.confirmPayment({
      //`Elements` instance that was used to create the Payment Element
      elements,
      clientSecret,
      confirmParams: {
        return_url: "http://localhost:5173",
      },
    });

    if (error) {
      // This point will only be reached if there is an immediate error when
      // confirming the payment. Show error to your customer (for example, payment
      // details incomplete)
      setErrorMessage(error.message);
    } else {
      // Your customer will be redirected to your `return_url`. For some payment
      // methods like iDEAL, your customer will be redirected to an intermediate
      // site first to authorize the payment, then redirected to the `return_url`.
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <PaymentElement />
      <label>Amount (in $) :</label>
      <input
        type="number"
        name="amount"
        id="amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        className="amount-input"
      />
      <button
        type="submit"
        disabled={!stripe || !elements}
        className="submit-button"
      >
        Pay
      </button>
      {/* Show error message to your customers */}
      {errorMessage && <div className="error-message">{errorMessage}</div>}
    </form>
  );
}

export default Payment;
