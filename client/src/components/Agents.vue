<template>
  <div>
    <h2>Agents</h2>
    <ul>
      <li v-for="agent in agents" :key="agent.id">
        {{ agent.name }} - Orders: {{ agent.total_orders_delivered }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      agents: [],
    };
  },
  created() {
    this.fetchAgents();
  },
  methods: {
    async fetchAgents() {
      try {
        const response = await fetch('http://localhost:8000/agents');
        if (!response.ok) {
          throw new Error('Failed to fetch agents');
        }
        this.agents = await response.json();
      } catch (error) {
        console.error('Error fetching agents:', error);
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