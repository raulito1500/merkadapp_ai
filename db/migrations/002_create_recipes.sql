CREATE TABLE recipes (
	id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	identity_text text NOT NULL,
	embedding vector(384) NOT NULL,
	detail jsonb NOT NULL,
	created_at timestamptz NOT NULL DEFAULT now()
);
