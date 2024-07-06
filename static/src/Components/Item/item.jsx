import React from 'react'
import './item.css'
import { Link } from 'react-router-dom'

const item = (props) => {
  return (
    <div className='item'>
        <Link to={`/proct/${props.id}`}> <img src={props.image} alt="" /></Link>
        <p>{props.name}</p>
        <div className="item-prices">
            <div className="item-price-new">
                ${props.new_price}
            </div>
            <div className="item-price-old">
               $ {props.old_price}
            </div>
        </div>
    </div>
  )
}

export default item
