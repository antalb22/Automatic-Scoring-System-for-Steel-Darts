<script lang="ts">
    import {onMount} from "svelte";
    import {goto} from "$app/navigation";
    import Navbar from "$lib/components/Navbar.svelte";

    type Plan = { id: number; name: string };

    let plans: Plan[] = [];
    let newPlanName = "";

    async function loadPlans() {
        const res = await fetch("/api/training");
        plans = await res.json();
    }

    async function addPlan() {
        if (!newPlanName.trim()) return;
        await fetch("/api/training", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({name: newPlanName})
        });
        newPlanName = "";
        await loadPlans();
    }

    async function deletePlan(id: number) {
        if (!confirm("Are you sure you want to delete this plan?")) return;
        await fetch(`/api/training/${id}`, {method: "DELETE"});
        await loadPlans();
    }

    function openPlan(id: number) {
        goto(`/training/${id}`);
    }

    onMount(loadPlans);
</script>

<Navbar/>

<main>
    <div class="container">
        <h1>Training Plans</h1>

        <div class="new-plan">
            <input
                    bind:value={newPlanName}
                    placeholder="New training plan name"
                    type="text"
            />
            <button on:click={addPlan} type="button">Add</button>
        </div>

        <ul class="plans-list">
            {#each plans as plan}
                <li>
                    <button type="button" on:click={() => openPlan(plan.id)}>
                        <span>{plan.name}</span> <span class="id">(# {plan.id})</span>
                    </button>
                    <button class="delete" type="button" on:click={() => deletePlan(plan.id)}>Delete</button>
                </li>
            {/each}
        </ul>
    </div>
</main>

<style>
    main {
        display: flex;
        justify-content: center;
        margin-top: 2rem;
    }

    .container {
        width: 100%;
        max-width: 500px;
        background: #fff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }

    h1 {
        text-align: center;
        margin-bottom: 1.5rem;
        font-size: 2rem;
    }

    .new-plan {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
    }

    .new-plan input {
        flex: 1;
        padding: 0.5rem;
        border-radius: 6px;
        border: 1px solid #ccc;
    }

    .new-plan button {
        padding: 0.5rem 1rem;
        border-radius: 6px;
        background: #2563eb;
        color: white;
        border: none;
        cursor: pointer;
    }

    .new-plan button:hover {
        background: #1e40af;
    }

    .plans-list {
        list-style: none;
        padding: 0;
        margin: 0;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .plans-list li {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 6px;
        background: #f9f9f9;
    }

    .plans-list li button {
        background: none;
        border: none;
        cursor: pointer;
        padding: 0.3rem 0.5rem;
    }

    .plans-list li button:hover {
        background: rgba(0, 0, 0, 0.05);
    }

    .plans-list li .delete {
        background: #ef4444;
        color: white;
        border-radius: 6px;
        padding: 0.3rem 0.6rem;
    }

    .plans-list li .delete:hover {
        background: #b91c1c;
    }

    .id {
        color: #888;
        margin-left: 0.5rem;
    }
</style>
