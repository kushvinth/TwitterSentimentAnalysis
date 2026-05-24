const form = document.getElementById('analyze-form');
const statusNode = document.getElementById('status');
const results = document.getElementById('results');
const tweetList = document.getElementById('tweet-list');
let chart;

function setStatus(message, isError = false) {
  statusNode.textContent = message;
  statusNode.style.color = isError ? '#fca5a5' : '#bfdbfe';
}

function renderChart(breakdown) {
  const ctx = document.getElementById('sentiment-chart');
  const data = [breakdown.positive, breakdown.neutral, breakdown.negative];

  if (chart) {
    chart.destroy();
  }

  chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Positive', 'Neutral', 'Negative'],
      datasets: [{
        data,
        backgroundColor: ['#22c55e', '#f59e0b', '#ef4444'],
        borderWidth: 0,
      }],
    },
    options: {
      plugins: {
        legend: {
          labels: { color: '#eef2ff' },
        },
      },
    },
  });
}

function renderTweets(tweets) {
  tweetList.innerHTML = '';
  tweets.slice(0, 8).forEach((tweet) => {
    const card = document.createElement('article');
    card.className = `tweet-card ${tweet.sentiment}`;

    const textNode = document.createElement('div');
    textNode.textContent = tweet.tweet;

    const metaNode = document.createElement('div');
    metaNode.className = 'meta';
    metaNode.textContent = `${tweet.sentiment.toUpperCase()} • polarity ${tweet.polarity} • ${new Date(tweet.created_at).toLocaleString()}`;

    card.appendChild(textNode);
    card.appendChild(metaNode);
    tweetList.appendChild(card);
  });
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  setStatus('Analyzing tweets...');

  const payload = {
    keyword: document.getElementById('keyword').value,
    count: Number(document.getElementById('count').value),
  };

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to analyze tweets.');
    }

    document.getElementById('total-tweets').textContent = data.count;
    document.getElementById('avg-polarity').textContent = data.average_polarity;
    document.getElementById('avg-subjectivity').textContent = data.average_subjectivity;

    renderChart(data.sentiment_breakdown);
    renderTweets(data.tweets);

    setStatus(`Showing live sentiment for "${data.keyword}".`);
    results.classList.remove('hidden');
  } catch (error) {
    setStatus(error.message, true);
    results.classList.add('hidden');
  }
});
