<template>
    <div>
      <h2>Orders</h2>
      <ul>
        <li v-for="order in orders" :key="order.id">
          {{ order.address }} - Status: {{ order.status }}
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        orders: [],
      };
    },
    created() {
      this.fetchOrders();
    },
    methods: {
      async fetchOrders() {
        try {
          const response = await fetch('http://localhost:8000/orders');
          if (!response.ok) {
            throw new Error('Failed to fetch orders');
          }
          this.orders = await response.json();
        } catch (error) {
          console.error('Error fetching orders:', error);
        }
      },
    },
  };
  </script>
  
  <style scoped>
  ul {
    list-style-type: none;
    padding: 0;
  }
  li {
    margin: 10px 0;
  }
  </style>