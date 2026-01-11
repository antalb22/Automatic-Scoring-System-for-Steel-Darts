<script lang="ts">
    import {onMount} from 'svelte';
    import {page} from '$app/stores';
    import Navbar from '$lib/components/Navbar.svelte';

    type Target = { id: number; value: number; type: "S" | "D" | "T"; order: number };
    let targets: Target[] = [];
    let newValue: number = 20;
    let newType: "S" | "D" | "T" = "S";

    let planId: number;
    let planName: string = "";

    $: planId = Number($page.params.id);

    const sectorValues: number[] = [...Array(20).keys()].map(i => i + 1);

    async function loadPlan() {
        const res = await fetch(`/api/training/${planId}`);
        const data = await res.json();
        planName = data.name;
        targets = data.targets || [];
        targets.sort((a, b) => a.order - b.order);
    }

    async function addTarget() {
        const res = await fetch(`/api/training/${planId}/targets`, {
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({value: newValue, type: newType})
        });
        const t: Target = await res.json();
        targets = [...targets, t].sort((a, b) => a.order - b.order);
    }

    async function deleteTarget(id: number) {
        await fetch(`/api/training/${planId}/targets/${id}`, {method: "DELETE"});
        targets = targets.filter(t => t.id !== id);
    }

    onMount(loadPlan);
</script>

<Navbar/>

<main class="container">
    <h1>Editing: {planName}</h1>

    <div class="add-target">
        <select bind:value={newType} disabled={newValue === 25 || newValue === 50}>
            <option value="S">Single</option>
            <option value="D">Double</option>
            <option value="T">Triple</option>
        </select>

        <select bind:value={newValue}>
            {#each sectorValues as val}
                <option value={val}>{val}</option>
            {/each}
            <option value={25}>25 (Bull)</option>
            <option value={50}>50 (Bull Double)</option>
        </select>

        <button on:click={addTarget} type="button">Add Target</button>
    </div>

    <ul class="target-list">
        {#each targets as t (t.id)}
            <li>
                {t.type}-{t.value} (Order: {t.order})
                <button class="delete" on:click={() => deleteTarget(t.id)}>Delete</button>
            </li>
        {/each}
    </ul>
</main>

<style>
    main.container {
        max-width: 500px;
        margin: 2rem auto;
        padding: 2rem;
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        text-align: center;
    }

    h1 {
        margin-bottom: 1.5rem;
    }

    .add-target {
        display: flex;
        gap: 0.5rem;
        justify-content: center;
        margin-bottom: 1.5rem;
    }

    select {
        padding: 0.5rem;
        border-radius: 6px;
        border: 1px solid #ccc;
    }

    button {
        padding: 0.5rem 1rem;
        border-radius: 6px;
        background: #2563eb;
        color: white;
        border: none;
        cursor: pointer;
    }

    button:hover {
        background: #1e40af;
    }

    .target-list {
        list-style: none;
        padding: 0;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
    }

    .target-list li {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 6px;
        background: #f9f9f9;
    }

    .target-list li .delete {
        background: #ef4444;
        color: white;
        border-radius: 6px;
        padding: 0.3rem 0.6rem;
        border: none;
        cursor: pointer;
    }

    .target-list li .delete:hover {
        background: #b91c1c;
    }

</style>
