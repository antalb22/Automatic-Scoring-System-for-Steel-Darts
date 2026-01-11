<script lang="ts">
    export let throws: any[] = [];
    export let optimalTarget: { x: number, y: number } | null = null;
    export let sigma: { x: number, y: number } | null = null;

    const BULL_RADIUS = 0.635;
    const OUTER_BULL_RADIUS = 1.59;
    const TRIPLE_RING_RADIUS = 10.7;
    const DOUBLE_RING_RADIUS = 17.0;

    const SVG_SIZE = 300;
    const CENTER = SVG_SIZE / 2;
    const SCALE = 7.5;

    function mapX(cm: number) {
        return CENTER + (cm * SCALE);
    }

    function mapY(cm: number) {
        return CENTER - (cm * SCALE);
    }
</script>

<div class="heatmap-container">
    <h3>Throw Distribution & Tip</h3>

    <svg height={SVG_SIZE} viewBox="0 0 {SVG_SIZE} {SVG_SIZE}" width={SVG_SIZE}>
        <circle cx={CENTER} cy={CENTER} fill="#111" r={22 * SCALE}/>

        {#each Array(20) as _, i}
            {@const angleDeg = i * 18 + 9}
            {@const angleRad = angleDeg * (Math.PI / 180)}
            {@const rPix = DOUBLE_RING_RADIUS * SCALE}

            <line
                    x1={CENTER}
                    y1={CENTER}
                    x2={CENTER + rPix * Math.cos(angleRad)}
                    y2={CENTER - rPix * Math.sin(angleRad)}
                    stroke="#333"
                    stroke-width="1"
            />
        {/each}

        <circle cx={CENTER} cy={CENTER} fill="none" r={DOUBLE_RING_RADIUS * SCALE} stroke="#555" stroke-width="2"/>
        <circle cx={CENTER} cy={CENTER} fill="none" r={TRIPLE_RING_RADIUS * SCALE} stroke="#555" stroke-width="2"/>
        <circle cx={CENTER} cy={CENTER} fill="none" r={OUTER_BULL_RADIUS * SCALE} stroke="green" stroke-width="1"/>
        <circle cx={CENTER} cy={CENTER} fill="red" r={BULL_RADIUS * SCALE}/>

        {#each throws as t}
            {#if t.x !== null && t.y !== null && t.x !== undefined}
                <circle
                        cx={mapX(t.x)}
                        cy={mapY(t.y)}
                        r="3"
                        fill="#FFD700"
                        opacity="0.6"
                />
            {/if}
        {/each}

        {#if optimalTarget && sigma}
            <ellipse
                    cx={mapX(optimalTarget.x)}
                    cy={mapY(optimalTarget.y)}
                    rx={sigma.x * 2 * SCALE}
                    ry={sigma.y * 2 * SCALE}
                    fill="cyan"
                    fill-opacity="0.2"
                    stroke="cyan"
                    stroke-width="1"
                    stroke-dasharray="4"
            />
        {/if}

        {#if optimalTarget}
            <g transform="translate({mapX(optimalTarget.x)}, {mapY(optimalTarget.y)})">
                <line x1="-6" y1="-6" x2="6" y2="6" stroke="#00FFFF" stroke-width="3"/>
                <line x1="6" y1="-6" x2="-6" y2="6" stroke="#00FFFF" stroke-width="3"/>
            </g>
        {/if}
    </svg>

    <div class="legend">
        <span style="color: #FFD700">● Throws</span>
        <span style="color: #00FFFF">✕ Recommended Target</span>
    </div>
</div>

<style>
    .heatmap-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-top: 20px;
        background: #222;
        padding: 15px;
        border-radius: 12px;
        color: white;
    }

    h3 {
        margin-bottom: 10px;
        color: #eee;
        font-size: 1.1rem;
    }

    .legend {
        margin-top: 10px;
        font-size: 0.8rem;
        display: flex;
        gap: 15px;
    }
</style>