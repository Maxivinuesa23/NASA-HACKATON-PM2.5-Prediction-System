import React from 'react';

// --- Componente de Efecto Estelar (Partículas CSS) ---
const AtmosphereEffect = () => (
  // Fondo de espacio profundo y fijo
  <div className="absolute top-0 left-0 w-full h-full pointer-events-none overflow-hidden z-0 bg-gray-950">
    <style jsx="true">{`
      /* Animación de brillo y movimiento lento de las "estrellas" */
      @keyframes twinkle {
        0%,
        100% {
          transform: translate(0, 0) scale(0.8);
          opacity: 0.6;
        }
        50% {
          transform: translate(-10px, 15px) scale(1.2);
          opacity: 1;
        }
      }
      @keyframes floatSlow {
        0% {
          transform: translate(0, 0);
        }
        50% {
          transform: translate(15px, 25px);
        }
        100% {
          transform: translate(0, 0);
        }
      }

      .star-system span {
        position: absolute;
        width: 3px;
        height: 3px;
        background-color: rgba(255, 255, 255, 0.8); /* Estrellas blancas */
        border-radius: 50%;
        box-shadow: 0 0 5px rgba(255, 255, 255, 0.5); /* Sombra para simular brillo */
        animation: twinkle 10s infinite alternate ease-in-out,
          floatSlow 30s infinite ease-in-out;
        opacity: 0.8;
      }

      /* Posicionamiento aleatorio de las estrellas */
      .star-system span:nth-child(1) {
        top: 10%;
        left: 5%;
        animation-duration: 8s;
        animation-delay: 0s;
      }
      .star-system span:nth-child(2) {
        top: 25%;
        left: 20%;
        animation-duration: 12s;
        animation-delay: 1s;
      }
      .star-system span:nth-child(3) {
        top: 40%;
        left: 10%;
        animation-duration: 9s;
        animation-delay: 2s;
      }
      .star-system span:nth-child(4) {
        top: 60%;
        left: 35%;
        animation-duration: 15s;
        animation-delay: 3s;
      }
      .star-system span:nth-child(5) {
        top: 80%;
        left: 50%;
        animation-duration: 7s;
        animation-delay: 4s;
      }
      .star-system span:nth-child(6) {
        top: 5%;
        left: 60%;
        animation-duration: 18s;
        animation-delay: 5s;
      }
      .star-system span:nth-child(7) {
        top: 50%;
        left: 85%;
        animation-duration: 11s;
        animation-delay: 6s;
      }
      .star-system span:nth-child(8) {
        top: 75%;
        left: 70%;
        animation-duration: 13s;
        animation-delay: 7s;
      }
      .star-system span:nth-child(9) {
        top: 90%;
        left: 95%;
        animation-duration: 16s;
        animation-delay: 8s;
      }
      .star-system span:nth-child(10) {
        top: 30%;
        left: 75%;
        animation-duration: 10s;
        animation-delay: 9s;
      }
      /* Agrega más estrellas para densidad */
      .star-system span:nth-child(11) {
        top: 15%;
        left: 45%;
        animation-duration: 14s;
        animation-delay: 1s;
      }
      .star-system span:nth-child(12) {
        top: 65%;
        left: 15%;
        animation-duration: 17s;
        animation-delay: 5s;
      }
      .star-system span:nth-child(13) {
        top: 45%;
        left: 55%;
        animation-duration: 9s;
        animation-delay: 2s;
      }
      .star-system span:nth-child(14) {
        top: 20%;
        left: 80%;
        animation-duration: 12s;
        animation-delay: 4s;
      }
      .star-system span:nth-child(15) {
        top: 85%;
        left: 5%;
        animation-duration: 15s;
        animation-delay: 6s;
      }
    `}</style>

    {/* Sistema de Partículas/Estrellas */}
    <div className="star-system w-full h-full">
      <span></span>
      <span></span>
      <span></span>
      <span></span>
      <span></span>
      <span></span>
      <span></span>
      <span></span>
      <span></span>
      <span></span>
      <span></span>
      <span></span>
      <span></span>
      <span></span>
      <span></span>
    </div>

    {/* Brillo de fondo sutil (simulando nebulosa lejana) */}
    <div className="absolute top-0 left-0 w-full h-full pointer-events-none overflow-hidden z-10">
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500 opacity-5 rounded-full mix-blend-screen filter blur-3xl animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-cyan-500 opacity-5 rounded-full mix-blend-screen filter blur-3xl animate-pulse delay-500"></div>
    </div>
  </div>
);

export default AtmosphereEffect;