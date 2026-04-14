import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createJob, fetchRecipes } from "../lib/api";

type Recipe = {
  id: string;
  name: string;
  description: string;
};

export function IngestPage() {
  const navigate = useNavigate();
  const [sourceUrl, setSourceUrl] = useState("");
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [selectedRecipes, setSelectedRecipes] = useState<string[]>(["hot-take", "explainer-tip"]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRecipes()
      .then((payload) => setRecipes(payload.recipes))
      .catch((err: Error) => setError(err.message));
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const job = await createJob({ sourceUrl, recipeIds: selectedRecipes });
      navigate(`/jobs/${job.job.id}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  function toggleRecipe(recipeId: string) {
    setSelectedRecipes((current) =>
      current.includes(recipeId)
        ? current.filter((item) => item !== recipeId)
        : [...current, recipeId],
    );
  }

  return (
    <section className="panel hero-grid">
      <div className="hero-copy">
        <p className="eyebrow">Product Source of Truth</p>
        <h2>Paste a TikTok LIVE replay URL and let recipes find the strongest moments.</h2>
        <p>
          KiniVideo is built around creator approval, not blind automation. Recipes score
          different moment types so you can review sharper clips faster.
        </p>
      </div>

      <form className="ingest-form" onSubmit={handleSubmit}>
        <label>
          TikTok Replay URL
          <input
            type="url"
            required
            value={sourceUrl}
            placeholder="https://www.tiktok.com/..."
            onChange={(event) => setSourceUrl(event.target.value)}
          />
        </label>

        <fieldset>
          <legend>Clip Recipes</legend>
          <div className="recipe-grid">
            {recipes.map((recipe) => (
              <button
                key={recipe.id}
                type="button"
                className={selectedRecipes.includes(recipe.id) ? "recipe-card active" : "recipe-card"}
                onClick={() => toggleRecipe(recipe.id)}
              >
                <strong>{recipe.name}</strong>
                <span>{recipe.description}</span>
              </button>
            ))}
          </div>
        </fieldset>

        {error ? <p className="error">{error}</p> : null}

        <button className="primary-button" type="submit" disabled={submitting}>
          {submitting ? "Creating job..." : "Create clipping job"}
        </button>
      </form>
    </section>
  );
}
