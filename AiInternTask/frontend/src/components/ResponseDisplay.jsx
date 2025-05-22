import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import FormatQuoteIcon from '@mui/icons-material/FormatQuote';
import TocIcon from '@mui/icons-material/Toc';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import DescriptionIcon from '@mui/icons-material/Description';

const ResponseDisplay = ({ response }) => {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Query: {response.query_text}
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="response tabs">
          <Tab icon={<AutoAwesomeIcon />} label="Themes" />
          <Tab icon={<TocIcon />} label="Document Responses" />
        </Tabs>
      </Box>

      {/* Themes Tab */}
      {tabValue === 0 && (
        <Box>
          {response.themes.length === 0 ? (
            <Typography variant="body1" color="textSecondary" sx={{ p: 2 }}>
              No common themes identified across documents.
            </Typography>
          ) : response.themes.length === 1 && response.themes[0].theme_name === "Single Document" ? (
            <Box sx={{ p: 2, bgcolor: 'primary.light', borderRadius: 2, mb: 2 }}>
              <Typography variant="subtitle1" color="primary.dark" gutterBottom>
                <AutoAwesomeIcon fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} />
                {response.themes[0].theme_name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {response.themes[0].description}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1, fontStyle: 'italic' }}>
                {response.themes[0].supporting_evidence[0]}
              </Typography>
            </Box>
          ) : (
            response.themes.map((theme, index) => (
              <Paper key={index} elevation={2} sx={{ p: 2, mb: 2, borderLeft: '4px solid', borderColor: 'primary.main' }}>
                <Typography variant="h6" color="primary" gutterBottom>
                  <AutoAwesomeIcon fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} />
                  {theme.theme_name}
                </Typography>

                <Typography variant="body1" paragraph>
                  {theme.description}
                </Typography>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <TocIcon fontSize="small" sx={{ mr: 1 }} />
                    Documents:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {theme.document_ids.map((docId, i) => {
                      // Find the document title from the responses
                      const docTitle = response.document_responses.find(dr => dr.document_id === docId)?.document_title || docId;
                      return (
                        <Chip
                          key={i}
                          label={docTitle}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      );
                    })}
                  </Box>
                </Box>

                <Box>
                  <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <FormatQuoteIcon fontSize="small" sx={{ mr: 1 }} />
                    Supporting Evidence:
                  </Typography>
                  <Box sx={{ pl: 2, borderLeft: '2px solid', borderColor: 'grey.300', ml: 1 }}>
                    {theme.supporting_evidence.map((evidence, i) => (
                      <Typography key={i} variant="body2" paragraph>
                        • {evidence}
                      </Typography>
                    ))}
                  </Box>
                </Box>
              </Paper>
            ))
          )}
        </Box>
      )}

      {/* Document Responses Tab */}
      {tabValue === 1 && (
        <Box>
          {response.document_responses.map((docResponse, index) => (
            <Accordion
              key={index}
              sx={{
                mb: 2,
                '&.Mui-expanded': {
                  borderLeft: '4px solid',
                  borderColor: 'primary.main',
                }
              }}
              defaultExpanded={response.document_responses.length === 1}
            >
              <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                sx={{
                  '&.Mui-expanded': {
                    bgcolor: 'primary.light',
                  }
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                  <DescriptionIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
                    {docResponse.document_title}
                  </Typography>
                  {docResponse.citations.length > 0 && (
                    <Chip
                      size="small"
                      label={`${docResponse.citations.length} citation${docResponse.citations.length > 1 ? 's' : ''}`}
                      color="secondary"
                      variant="outlined"
                      sx={{ ml: 1 }}
                    />
                  )}
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Paper
                  variant="outlined"
                  sx={{
                    p: 2,
                    mb: 2,
                    bgcolor: 'background.paper',
                    borderLeft: '3px solid',
                    borderColor: 'primary.light'
                  }}
                >
                  <Typography variant="body1" paragraph>
                    {docResponse.extracted_answer}
                  </Typography>
                </Paper>

                {docResponse.citations.length > 0 && (
                  <Box>
                    <Typography variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <FormatQuoteIcon fontSize="small" sx={{ mr: 1 }} />
                      Citations:
                    </Typography>

                    <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
                      <Table size="small">
                        <TableHead>
                          <TableRow sx={{ bgcolor: 'primary.light' }}>
                            <TableCell>Page</TableCell>
                            <TableCell>Paragraph</TableCell>
                            <TableCell>Text</TableCell>
                            <TableCell align="center">Relevance</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {docResponse.citations.map((citation, i) => (
                            <TableRow key={i} hover>
                              <TableCell>{citation.page_number || 'N/A'}</TableCell>
                              <TableCell>{citation.paragraph || 'N/A'}</TableCell>
                              <TableCell sx={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                                  "{citation.sentence || 'N/A'}"
                                </Typography>
                              </TableCell>
                              <TableCell align="center">
                                {citation.relevance_score ? (
                                  <Chip
                                    size="small"
                                    label={`${(citation.relevance_score * 100).toFixed(0)}%`}
                                    color={citation.relevance_score > 0.8 ? "success" :
                                           citation.relevance_score > 0.5 ? "primary" : "default"}
                                    variant="outlined"
                                  />
                                ) : 'N/A'}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Box>
                )}
              </AccordionDetails>
            </Accordion>
          ))}
        </Box>
      )}
    </Box>
  );
};

export default ResponseDisplay;
