import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { MapPin } from "lucide-react";
import L from "leaflet";

// Correção para ícones do Leaflet no React
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

interface DestinationMapProps {
  destination: string;
}

// Componente auxiliar para atualizar o centro do mapa
function ChangeView({ center }: { center: [number, number] }) {
  const map = useMap();
  map.setView(center, 13);
  return null;
}

export default function DestinationMap({ destination }: DestinationMapProps) {
  const [position, setPosition] = useState<[number, number] | null>(null);

  useEffect(() => {
    if (!destination) return;

    // Geocoding simples usando OpenStreetMap (Nominatim)
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(destination)}`)
      .then((res) => res.json())
      .then((data) => {
        if (data && data.length > 0) {
          setPosition([parseFloat(data[0].lat), parseFloat(data[0].lon)]);
        }
      })
      .catch((err) => console.error("Erro ao buscar coordenadas:", err));
  }, [destination]);

  if (!position) return null;

  return (
    <div className="h-[300px] w-full rounded-lg overflow-hidden border shadow-sm my-6 z-0 relative">
      <MapContainer center={position} zoom={13} scrollWheelZoom={false} className="h-full w-full z-0">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={position}>
          <Popup>{destination}</Popup>
        </Marker>
        <ChangeView center={position} />
      </MapContainer>
    </div>
  );
}