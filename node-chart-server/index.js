

const express = require("express");
const { ChartJSNodeCanvas } = require("chartjs-node-canvas");
const dayjs = require("dayjs");

const app = express();
const PORT = 3000;

// Middleware to read JSON body
app.use(express.json());

// Chart renderer setup
const chartJSNodeCanvas = new ChartJSNodeCanvas({
  width: 900,
  height: 450,
  backgroundColour: "white"
});

// Health check
app.get("/", (req, res) => {
  res.send("Chart server is running 🚀");
});

// ---- CHART ENDPOINT ----
app.post("/render-chart", async (req, res) => {
  try {
    const { metric_name, unit, series } = req.body;

    if (!series || !Array.isArray(series)) {
      return res.status(400).json({ error: "Invalid time series input" });
    }

    // Prepare chart data
    const labels = series.map(p =>
      dayjs(p.date).format("YYYY-MM-DD")
    );

    const values = series.map(p => p.value);

    const chartConfig = {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: `${metric_name || "Metric"} (${unit || ""})`,
            data: values,
            borderColor: "#2563eb",
            borderWidth: 2,
            pointRadius: 3,
            tension: 0.3
          }
        ]
      },
      options: {
        responsive: false,
        plugins: {
          legend: { display: true }
        },
        scales: {
          x: {
            title: { display: true, text: "Date" }
          },
          y: {
            title: { display: true, text: unit || "Value" }
          }
        }
      }
    };

    // Render image
    const imageBuffer = await chartJSNodeCanvas.renderToBuffer(chartConfig);


     // 👇 IMPORTANT PART
    res.set("Content-Type", "image/png");
    res.send(imageBuffer);

  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
