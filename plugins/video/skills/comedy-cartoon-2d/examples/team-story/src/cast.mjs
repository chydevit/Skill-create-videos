// This film's cast looks (the first Bong Smei / Bong Nimith / Devit designs). They are registered over the
// template's CAST, so this film keeps its original look; the series cast in people.mjs moved on from these.
import { CAST } from './people.mjs';

Object.assign(CAST, {
  smei: { // stocky, round belly, bulb nose
    H: 400, legs: 0.30, torso: 0.30, headS: 1.62, hx: 1.06, hy: 1.0, belly: 0.65, arm: 64, nose: 'bulb',
    sw: 58, ww: 64, skin: '#c98b5e', skinD: '#a86e46', hair: '#2a2426', gray: '#b9b4b4', beard: true,
    shirt: '#2e8a57', shirtD: '#1f6b42', collar: '#45a56f', pants: '#c9a46a', pantsD: '#a8834d', shoe: '#5a3a28', style: 'polo', hairStyle: 'short', eyeSize: 1.05,
  },
  nimith: { // tall and lanky, long neck, pointy nose (the "Marge" silhouette)
    H: 475, legs: 0.47, torso: 0.29, headS: 1.42, hx: 0.9, hy: 1.12, belly: 0, arm: 80, nose: 'point', neck: 26,
    sw: 38, ww: 30, skin: '#e0a378', skinD: '#c4865c', hair: '#1f1a22', glasses: true,
    shirt: '#5aa8ec', shirtD: '#3f8bd0', collar: '#8cc6f7', pants: '#2d3a6b', pantsD: '#1e2750', shoe: '#2a2633', style: 'shirt', hairStyle: 'neat', eyeSize: 1.1,
  },
  devit: { // short, round and bouncy, giant head (the "Benny" silhouette)
    H: 330, legs: 0.26, torso: 0.27, headS: 1.8, hx: 1.05, hy: 1.0, belly: 0.3, arm: 52, nose: 'button',
    sw: 46, ww: 50, skin: '#d4955f', skinD: '#b5773f', hair: '#1f1c22', headphones: true,
    shirt: '#f2823a', shirtD: '#d0632a', collar: '#ffb070', pants: '#3f6fbf', pantsD: '#2f569a', shoe: '#ffffff', style: 'hoodie', hairStyle: 'messy', eyeSize: 1.3,
  },
});
