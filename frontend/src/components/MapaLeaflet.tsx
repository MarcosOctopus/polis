'use client';

import { useEffect, useState, useMemo } from 'react';
import { MapContainer, TileLayer, Polygon, Marker, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// ── Fix default icon ──
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// ── Types ──
export interface NeighborhoodGeo {
  id: string;
  nome: string;
  coordinates: [number, number][];
  centro: [number, number];
}

export interface NdMapItem {
  neighborhood: NeighborhoodGeo;
  count: number;
}

// ── MapController: fly to selected neighborhood ──
function MapController({ center, zoom }: { center: [number, number] | null; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    if (center) map.flyTo(center, zoom, { duration: 1 });
    else map.flyTo([-20.329, -40.287], 12.5, { duration: 1 });
  }, [center, zoom, map]);
  return null;
}

// ── NumberedMarker: bolinha numerada ──
interface MarkerProps {
  center: [number, number];
  count: number;
  color: string;
  isSelected: boolean;
  isHovered: boolean;
  onClick: () => void;
  onMouseOver: () => void;
  onMouseOut: () => void;
}

function NumberedMarker({ center, count, color, isSelected, isHovered, onClick, onMouseOver, onMouseOut }: MarkerProps) {
  const icon = useMemo(() => L.divIcon({
    className: '',
    html: `<div style="
      width:52px;height:52px;border-radius:50%;
      display:flex;align-items:center;justify-content:center;
      background:${color};color:#fff;
      font-size:15px;font-weight:800;font-family:system-ui;
      box-shadow:0 0 0 ${isSelected ? 4 : isHovered ? 3 : 2}px rgba(255,255,255,0.5),
                 0 4px 12px rgba(0,0,0,0.5);
      border:${isSelected ? '3px solid #22d3ee' : isHovered ? '2px solid #a78bfa' : '2px solid rgba(255,255,255,0.4)'};
      transition:all 0.15s;
      cursor:pointer;
      transform:scale(${isSelected ? 1.15 : isHovered ? 1.08 : 1});
    ">${count}</div>`,
    iconSize: [52, 52],
    iconAnchor: [26, 26],
  }), [count, color, isSelected, isHovered]);

  return (
    <Marker
      position={center}
      icon={icon}
      eventHandlers={{
        click: onClick,
        mouseover: onMouseOver,
        mouseout: onMouseOut,
      }}
    />
  );
}

interface Props {
  centro: [number, number];
  zoom: number;
  ndMap: NdMapItem[];
  selected: string | null;
  hovered: string | null;
  onPolygonClick: (id: string, nome: string) => void;
  onHoverChange: (id: string | null) => void;
  getFillColor: (count: number) => string;
  getStrokeColor: (id: string) => string;
  getMarkerColor: (count: number) => string;
}

export default function MapaLeaflet({
  centro, zoom, ndMap,
  selected, hovered,
  onPolygonClick, onHoverChange,
  getFillColor, getStrokeColor, getMarkerColor,
}: Props) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);

  if (!mounted) {
    return (
      <div className="w-full h-[520px] rounded-xl bg-[#0a0a0f] flex items-center justify-center">
        <div className="text-gray-600 text-sm">Carregando mapa...</div>
      </div>
    );
  }

  const selPos = selected
    ? ndMap.find(n => n.neighborhood.id === selected)?.neighborhood.centro ?? null
    : null;

  return (
    <MapContainer
      center={centro}
      zoom={zoom}
      className="w-full h-[520px] rounded-xl"
      zoomControl={false}
      scrollWheelZoom={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
      />
      <MapController center={selPos as any} zoom={zoom} />

      {/* Neighborhood polygons */}
      {ndMap.map((nd) => {
        const isSel = selected === nd.neighborhood.id;
        const isHov = hovered === nd.neighborhood.id;
        return (
          <Polygon
            key={nd.neighborhood.id}
            positions={nd.neighborhood.coordinates}
            pathOptions={{
              fillColor: getFillColor(nd.count),
              fillOpacity: isSel ? 0.55 : isHov ? 0.45 : 0.25,
              color: getStrokeColor(nd.neighborhood.id),
              weight: isSel ? 3 : isHov ? 2.5 : 1.5,
              opacity: 1,
            }}
            eventHandlers={{
              click: () => onPolygonClick(nd.neighborhood.id, nd.neighborhood.nome),
              mouseover: () => onHoverChange(nd.neighborhood.id),
              mouseout: () => onHoverChange(null),
            }}
          />
        );
      })}

      {/* Numbered circle markers */}
      {ndMap.map((nd) => (
        <NumberedMarker
          key={`mkr-${nd.neighborhood.id}`}
          center={nd.neighborhood.centro}
          count={nd.count}
          color={getMarkerColor(nd.count)}
          isSelected={selected === nd.neighborhood.id}
          isHovered={hovered === nd.neighborhood.id}
          onClick={() => onPolygonClick(nd.neighborhood.id, nd.neighborhood.nome)}
          onMouseOver={() => onHoverChange(nd.neighborhood.id)}
          onMouseOut={() => onHoverChange(null)}
        />
      ))}
    </MapContainer>
  );
}
