import React from 'react'
import './ProductDisplay.css'
import star_icon from '../Assets/star_icon.png'
import star_dull_icon from '../Assets/star_dull_icon.png'


const ProductDisplay = (props) => {
  const {product} = props;
  return (
    <div className='productdisplay'>
        <div className="productdisplay-left">
          <div className="productdisplay-img-list">
            <img src={product.image} alt="" />
            <img src={product.image} alt="" />
            <img src={product.image} alt="" />
            <img src={product.image} alt="" />
          </div>
          <div className="productdisplay-img">
            <img className='productdisplay-main-img' src={product.image} alt="" />
          </div>
        </div>
        <div className="productdisplay-right">
          <h1>{product.name}</h1>
          <div className="productdisplaay-right-star">
            <img src={star_icon} alt="" />
            <img src={star_icon} alt="" />
            <img src={star_icon} alt="" />
            <img src={star_icon} alt="" />
            <img src={star_dull_icon} alt="" />
            <p>(122)</p>
          </div>
          <div className="productdisplay-right-prices">
            <div className="productdisplay-right-price-old">${product.old_price}</div>
            <div className="productdisplay-right-price-new">${product.new_price}</div>
          </div>
          <div className="productdisplay-right-description">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Veniam blanditiis optio libero, culpa eligendi explicabo ipsam ratione mollitia quibusdam recusandae?
          </div>
          <div className="productdisplay-righi-size">
            <h1>Select Size</h1>
              <div className="productdisplay-right-size">
                <div>S</div>
                <div>M</div>
                <div>L</div>
                <div>Xl</div>
                <div>XXL</div>
              </div>
          </div>
          <button>ADD TO CART</button>
          <p className='productdisplay-right-category'><span>Category :</span>Women, T-shirt, Crop Top</p>
          <p className='productdisplay-right-category'><span>Tags :</span>Modern, Latest</p>

        </div>
    </div>
  )
}

export default ProductDisplay