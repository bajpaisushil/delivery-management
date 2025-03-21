<template>
  <div id="app">
    <h1>Delivery Management System</h1>
    <Agents />
    <Orders />
  </div>
</template>

<script>
import Agents from './components/Agents.vue';
import Orders from './components/Orders.vue';

export default {
  name: 'App',
  components: {
    Agents,
    Orders,
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>