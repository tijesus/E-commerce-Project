import React from 'react'
import './Newsletter.css'

const Newsletter = () => {
  return (
    <div className='newsletter'>
        <h1>GET ECXCLUSIVE OFFERS ON YOUR EMAIL</h1>
        <p>subscribe to our newsletter to stay updated</p>
        <div>
            <input type="email" placeholder='example@mail.com' />
            <button>Subscribe</button>
        </div>
    </div>
  )
}

export default Newsletter