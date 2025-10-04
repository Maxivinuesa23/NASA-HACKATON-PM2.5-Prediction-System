import React from 'react';
import { ArrowUpRight } from 'lucide-react';

// Componente de Utilidad para formatear números de forma limpia
const formatNumber = (num) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + "k";
  }
  return num;
};

// Componente de Tarjeta de Métrica Animada (Tema oscuro)
const MetricCard = ({ title, value, unit, icon: Icon, change }) => {
  const isPositive = change >= 0;

  return (
    <div
      className="
      relative bg-gray-800/70 p-6 rounded-2xl shadow-2xl backdrop-blur-sm border border-gray-700
      transition duration-300 ease-in-out transform hover:scale-[1.02] hover:shadow-cyan-500/20
      w-full
    "
    >
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-400 uppercase tracking-widest">
          {title}
        </h3>
        <Icon className="w-5 h-5 text-cyan-400" />
      </div>

      <div className="mt-4 flex flex-col">
        <div className="text-4xl font-extrabold text-white">
          {formatNumber(value)}
          {unit}
        </div>
        <div
          className={`mt-2 flex items-center text-sm font-semibold ${
            isPositive ? "text-green-400" : "text-red-400"
          }`}
        >
          <ArrowUpRight
            className={`w-4 h-4 mr-1 transform ${
              isPositive ? "rotate-0" : "rotate-180 text-red-400"
            }`}
          />
          {change.toFixed(1)}%
          <span className="ml-2 font-normal text-gray-400">vs. mes pasado</span>
        </div>
      </div>
    </div>
  );
};

export default MetricCard;