# E-commerce Tech Store — Product Roadmap & User Stories

Proyecto: **Tienda online de productos tecnológicos**
Stack principal:

- Frontend: Next.js + React + Tailwind
- Backend: NestJS
- Database: PostgreSQL
- Pagos: Mercado Pago
- Envíos: Andreani
- IA: Vercel AI SDK + Groq
- Bot: WhatsApp Business API

Este documento define **todas las user stories del proyecto** para desarrollar el sistema **de forma incremental**, con buenas prácticas y **tests en frontend y backend**.

---

# 1. Fase 0 — Setup del Proyecto

Objetivo: tener una base sólida del proyecto.

## User Stories

### US-0.1 — Crear repositorio del proyecto [x]

**Como** desarrollador
**Quiero** crear un repositorio base
**Para** comenzar el desarrollo organizado.

**Criterios de aceptación**

- Repo inicializado
- README base
- Licencia
- .gitignore

---

### US-0.2 — Crear estructura del monorepo [x]

**Como** desarrollador
**Quiero** separar frontend y backend
**Para** mantener el proyecto organizado.

```
apps/
  web/
  api/

packages/
  ui/
  config/
```

---

### US-0.3 — Setup del Frontend [x]

**Como** desarrollador
**Quiero** crear la app de Next.js
**Para** desarrollar la tienda.

Criterios:

- Next.js instalado
- Tailwind configurado
- layout base
- estructura inicial

---

### US-0.4 — Setup del Backend [x]

**Como** desarrollador
**Quiero** crear la API en NestJS
**Para** manejar lógica del sistema.

Criterios:

- NestJS inicializado
- conexión a PostgreSQL
- estructura modular

---

### US-0.5 — Configuración de base de datos

Tablas iniciales:

```
products
categories
orders
order_items
payments
shipments
```

---

# 2. Fase 1 — Catálogo de Productos

Objetivo: poder **mostrar productos en la tienda**.

---

## US-1.1 — Crear modelo de producto

**Como** administrador
**Quiero** poder registrar productos
**Para** venderlos en la tienda.

Campos:

```
id
name
description
price
stock
image
category_id
created_at
```

---

## US-1.2 — Endpoint para listar productos

**Como** cliente
**Quiero** ver los productos disponibles
**Para** poder comprarlos.

Endpoint:

```
GET /products
```

---

## US-1.3 — Endpoint producto individual

```
GET /products/:slug
```

---

## US-1.4 — Mostrar productos en el frontend

Página:

```
/products
```

Mostrar:

- imagen
- nombre
- precio
- botón ver producto

---

## US-1.5 — Página de producto

Página:

```
/products/[slug]
```

Mostrar:

- imagen
- descripción
- precio
- stock
- botón agregar al carrito

---

# 3. Fase 2 — Carrito de Compras

Objetivo: permitir **seleccionar productos antes del checkout**.

---

## US-2.1 — Agregar producto al carrito

**Como** cliente
**Quiero** agregar productos al carrito
**Para** comprarlos después.

Estado del carrito en frontend:

```
cartItems
quantity
price
```

---

## US-2.2 — Ver carrito

Página:

```
/cart
```

Mostrar:

- productos
- cantidades
- subtotal

---

## US-2.3 — Modificar cantidad

El usuario puede:

- aumentar
- disminuir
- eliminar

---

## US-2.4 — Persistencia del carrito

Opciones:

- LocalStorage
- cookie

---

# 4. Fase 3 — Checkout

Objetivo: poder **crear pedidos**.

---

## US-3.1 — Formulario de checkout

Campos:

```
nombre
email
telefono
direccion
ciudad
codigo_postal
```

---

## US-3.2 — Crear orden

Endpoint:

```
POST /orders
```

Estados:

```
pending_payment
paid
shipped
delivered
```

---

## US-3.3 — Guardar productos del pedido

Tabla:

```
order_items
```

---

# 5. Fase 4 — Pagos

Objetivo: integrar pagos.

---

## US-4.1 — Crear preferencia de pago

Backend:

```
POST /payments/create
```

Devuelve:

```
checkout_url
```

---

## US-4.2 — Redirigir a pago

El frontend redirige al checkout.

---

## US-4.3 — Webhook de pago

Endpoint:

```
POST /webhooks/mercadopago
```

Actualizar orden:

```
pending_payment → paid
```

---

# 6. Fase 5 — Envíos

Objetivo: integrar logística.

---

## US-5.1 — Calcular costo de envío

```
POST /shipping/calculate
```

Datos:

```
postal_code
cart_items
```

---

## US-5.2 — Generar envío

Cuando el pago se confirma:

```
createShipment()
```

Guardar:

```
tracking_number
```

---

## US-5.3 — Mostrar tracking

Página:

```
/order/:id
```

---

# 7. Fase 6 — Panel de Administración

---

## US-6.1 — Login admin

Solo para administración.

---

## US-6.2 — CRUD de productos

Panel:

```
/admin/products
```

Acciones:

- crear
- editar
- eliminar

---

## US-6.3 — Ver pedidos

Panel:

```
/admin/orders
```

Mostrar:

- estado
- cliente
- total

---

# 8. Fase 7 — Asistente de IA

Objetivo: mejorar conversión.

---

## US-7.1 — Chat en la web

Componente:

```
AIChat
```

---

## US-7.2 — IA consulta productos

Tools del agente:

```
searchProducts()
getProduct()
```

---

## US-7.3 — IA recomienda productos

Ejemplo:

```
"Busco auriculares baratos"
```

Respuesta:

- lista de productos

---

# 9. Fase 8 — Bot de WhatsApp

---

## US-8.1 — Recibir mensajes

Webhook:

```
POST /whatsapp/webhook
```

---

## US-8.2 — IA responde preguntas

Ejemplos:

```
¿Tenés cargadores?
¿Cuánto cuesta el envío?
```

---

## US-8.3 — Generar link de pago

El bot puede enviar:

```
link de MercadoPago
```

---

# 10. Fase 9 — Inteligencia de Negocio

---

## US-9.1 — Dashboard de ventas

Mostrar:

- ventas del día
- productos más vendidos

---

## US-9.2 — Recomendador de productos con IA

IA analiza:

- ventas
- tendencias

---

## US-9.3 — Scraper de competencia

Servicio que guarda:

```
competitor_products
```

---

# 11. Testing Strategy (se definirá luego)

## Backend

Tests:

```
unit tests
integration tests
e2e tests
```

Framework:

```
Jest
```

---

## Frontend

Tests:

```
component tests
ui tests
e2e
```

Frameworks:

```
Vitest
Playwright
```

---

# Roadmap Simplificado

Orden recomendado de desarrollo:

```
1 Setup proyecto
2 Catálogo
3 Carrito
4 Checkout
5 Pagos
6 Envíos
7 Admin
8 IA web
9 Bot WhatsApp
10 Analytics
```

---

# Visión Final

El objetivo es construir una **tienda moderna con IA integrada**, donde:

- la web vende productos
- la IA recomienda productos
- el bot de WhatsApp vende automáticamente
- el sistema escala a futuro

Esto crea una **plataforma de e-commerce automatizada con IA**.
