<template>
  <div id="app">
    <h1>Delivery Management System</h1>

    <div>
      <h2>Actions</h2>
      <button @click="checkInAgent">Check-in Agent (Simulated)</button>
      <button @click="allocateOrders">Allocate Orders</button>
    </div>

    <div>
      <h2>Metrics</h2>
      <button @click="fetchMetrics">Refresh Metrics</button>
      <pre>{{ metrics }}</pre>
    </div>

    <div>
      <h2>Warehouses</h2>
      <button @click="fetchWarehouses">Refresh Warehouses</button>
      <pre>{{ warehouses }}</pre>
    </div>

    <div>
      <h2>Agents</h2>
      <button @click="fetchAgents">Refresh Agents</button>
      <pre>{{ agents }}</pre>
    </div>

    <div>
      <h2>Orders</h2>
      <button @click="fetchOrders">Refresh Orders</button>
      <pre>{{ orders }}</pre>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'App',
  data() {
    return {
      metrics: {},
      warehouses:[],
      agents:[],
      orders:[],
      backendUrl: 'http://127.0.0.1:8000'
    };
  },
  methods: {
    async checkInAgent() {
      // Simulate checking in the first agent for simplicity
      try {
        const response = await axios.post(`${this.backendUrl}/agents/checkin`, { agent_id: 1 });
        alert(response.data.message);
        this.fetchAgents();
      } catch (error) {
        alert('Error checking in agent');
        console.error(error);
      }
    },
    async allocateOrders() {
      try {
        const response = await axios.post(`${this.backendUrl}/allocate`);
        alert(response.data.message);
        this.fetchOrders();
        this.fetchMetrics();
      } catch (error) {
        alert('Error allocating orders');
        console.error(error);
      }
    },
    async fetchMetrics() {
      try {
        const response = await axios.get(`${this.backendUrl}/metrics`);
        this.metrics = response.data;
      } catch (error) {
        console.error('Error fetching metrics:', error);
        this.metrics = { error: 'Could not fetch metrics' };
      }
    },
    async fetchWarehouses() {
      try {
        const response = await axios.get(`${this.backendUrl}/warehouses`);
        this.warehouses = response.data;
      } catch (error) {
        console.error('Error fetching warehouses:', error);
        this.warehouses = [{ error: 'Could not fetch warehouses' }];
      }
    },
    async fetchAgents() {
      try {
        const response = await axios.get(`${this.backendUrl}/agents`);
        this.agents = response.data;
      } catch (error) {
        console.error('Error fetching agents:', error);
        this.agents = [{ error: 'Could not fetch agents' }];
      }
    },
    async fetchOrders() {
      try {
        const response = await axios.get(`${this.backendUrl}/orders`);
        this.orders = response.data;
      } catch (error) {
        console.error('Error fetching orders:', error);
        this.orders = [{ error: 'Could not fetch orders' }];
      }
    }
  },
  mounted() {
    this.fetchMetrics();
    this.fetchWarehouses();
    this.fetchAgents();
    this.fetchOrders();
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
h2 {
  margin-top: 20px;
}
button {
  margin: 5px;
  padding: 8px 15px;
  cursor: pointer;
}
pre {
  text-align: left;
  margin: 10px auto;
  padding: 15px;
  border: 1px solid #ccc;
  background-color: #f9f9f9;
  width: 80%;
  white-space: pre-wrap; /* Preserve newlines and spaces */
}
</style>