import React from 'react';
import './CSS/loginsignup.css'

export const LoginSignup = () => {
  return (
    <div className='loginsignup'>
      <div className="loginsignup-container">
        <h1>Sign up</h1>
        <div className="loginsignup-fields">
          <input type="text" placeholder='First Name' />
          <input type="text" placeholder='Last Name' />
          <input type="number" placeholder='Phone Number' />
          <input type="email" placeholder='Your Name' />
          <input type="password" placeholder='Password' />
          <input type="password" placeholder='Confirm Password' />
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
