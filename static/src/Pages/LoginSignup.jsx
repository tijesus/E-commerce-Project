import React from 'react';
import './CSS/loginsignup.css'

export const LoginSignup = () => {
  return (
    <div className='loginsignup'>
      <div className="loginsignup-container">
        <h1>Sign up</h1>
        <div className="loginsignup-fields">
          <input type="text" placeholder='First Name' required />
          <input type="text" placeholder='Last Name' required />
          <input type="number" placeholder='Phone Number' pattern='[0-9]{10}' required />
          {/* <input type="number" id="phone" name="phone" pattern="[0-9]{10}" placeholder="Enter 10-digit mobile number" required /> */}
          <input type="email" placeholder='Email' required />
          <input type="password" placeholder='Password' required />
          <input type="password" placeholder='Confirm Password' required />
        </div>
        <button>Continue</button>
        <p className='loginsignup-login'> Already have an account? <span>Login here</span></p>
        <div className="loginsignup-agree">
          <input type="checkbox" name='' id='' />
          <p>By continuing, i agree to the terms of use & privacy policy</p>
        </div>
      </div>
    </div>
  );
}
